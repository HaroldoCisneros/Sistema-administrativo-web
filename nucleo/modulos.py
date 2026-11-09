"""
nucleo/modulos.py
=================

Arma el menú del sistema a partir de los módulos instalados.

¿Cómo aparece un módulo en el menú?
    1. Está en settings.MODULOS_MENU (el orden de esa lista es el del menú).
    2. Su carpeta tiene un archivo menu.py con una variable MENU, así
       (ejemplo recortado de inventario/menu.py):

        from nucleo.modulos import opcion

        MENU = {
            "titulo": _("Inventory"),                 # nombre en pantalla (traducible)
            "descripcion": _("Items, warehouses..."), # texto debajo del nombre
            "icono": "inventario",                    # dibujo (nucleo/static/nucleo/img/iconos.svg)
            "color": "#0f766e",                       # color propio del módulo
            "opciones": {
                "tablas":    [opcion("articulos", _("Items")), ...],
                "procesos":  [...],
                "reportes":  [...],
                "consultas": [...],
            },
        }

    No hay que tocar nada más: este archivo recorre los módulos y junta sus
    menús. Más adelante aquí mismo se filtrará por los permisos de cada usuario
    (función menu()).

Las 4 secciones de cada módulo son fijas y se definen aquí abajo (SECCIONES).

Grupos: una opción puede tener sub-opciones (por ejemplo, Conteo Físico ›
Preparar y Cerrar / Ingresar Resultados). Se declaran con grupo() en vez de
opcion(); ver la función grupo() más abajo.

Opciones "pendientes":
    Una opción sin pantalla todavía (url=None) lleva a la página
    "Under construction" (nucleo/views.py, pendiente). Cuando se programe
    su pantalla, solo hay que ponerle la url en el menu.py del módulo:
        opcion("articulos", _("Items"), url="inventario:articulos")
"""

import copy                                  # para copiar el menú sin dañar el original
from functools import lru_cache              # guarda en memoria un resultado ya calculado
from importlib import import_module          # importa un archivo de Python por su nombre

from django.conf import settings             # la configuración (settings.py)
from django.urls import NoReverseMatch, reverse   # reverse: nombre de ruta -> dirección web
from django.utils import translation              # para traducir a un idioma fijo (buscador)
# gettext_lazy: marca el texto para traducir; se traduce al mostrarlo, con el idioma activo.
from django.utils.translation import gettext_lazy as _


# =============================================================================
# Las 4 secciones que tiene cada módulo (en este orden)
# =============================================================================
# clave       -> se usa en las direcciones (/inventario/tablas/...) y en el código
# titulo      -> lo que ve el usuario (en inglés; _() lo traduce al idioma de config.xml)
# subtitulo   -> explicación corta debajo del título
# icono       -> dibujo de la sección
SECCIONES = [
    {"clave": "tablas", "titulo": _("Tables"),
     "subtitulo": _("Master data and catalogs"), "icono": "tablas"},
    {"clave": "procesos", "titulo": _("Processes"),
     "subtitulo": _("Day-to-day transactions"), "icono": "procesos"},
    {"clave": "reportes", "titulo": _("Reports"),
     "subtitulo": _("Printable and exportable reports"), "icono": "reportes"},
    {"clave": "consultas", "titulo": _("Queries"),
     "subtitulo": _("Quick on-screen look-ups"), "icono": "consultas"},
]


def opcion(clave, titulo, url=None, ayuda="", compartida=None):
    """
    Crea una opción del menú. Se usa en el menu.py de cada módulo.

    clave  -> identificador corto, sin espacios (va en la dirección web).
    titulo -> texto que ve el usuario, en inglés y dentro de _() para que se
              traduzca: _("Customers"). La traducción va en el django.po del módulo.
    url    -> nombre de la ruta de su pantalla ("inventario:articulos").
              None = todavía no está hecha: lleva a "Under construction".
    ayuda  -> texto opcional que se muestra debajo del título.
    compartida -> si la opción es la MISMA pantalla que una opción de otro
              módulo, se indica cuál: "modulo:seccion:clave" (o, si está dentro
              de un grupo, "modulo:seccion:grupo:clave"). Ejemplo, en
              inventario/menu.py:
                  opcion("proveedores", _("Suppliers"), compartida="cxp:tablas:proveedores")
              Así hay un solo programa con dos accesos: la opción lleva a donde
              lleve la de Compras y Cuentas por Pagar (su pantalla o "en construcción").
              Cuando esa pantalla se programe, se activa en un solo lugar
              (cxp/menu.py) y aparece en los dos módulos.
    """
    return {"clave": clave, "titulo": titulo, "url": url, "ayuda": ayuda,
            "compartida": compartida, "grupo": False}


def grupo(clave, titulo, opciones):
    """
    Crea un GRUPO: una opción que no abre pantalla, sino que agrupa sub-opciones.
    Ejemplo (inventario/menu.py):

        grupo("conteo-fisico", _("Physical inventory count"), [
            opcion("preparar-cerrar", _("Prepare and close count")),
            opcion("ingresar-resultados", _("Enter count results")),
        ]),

    En el menú lateral se abre y cierra como una carpeta; en la página del
    módulo sale como título con sus sub-opciones debajo. Las sub-opciones en
    construcción quedan en /<modulo>/<seccion>/<grupo>/<opcion>/.
    """
    return {"clave": clave, "titulo": titulo, "grupo": True, "hijas": list(opciones)}


def hojas(seccion):
    """
    Todas las opciones de una sección que abren pantalla (las "hojas" del
    árbol): las sueltas y las que están dentro de un grupo, en orden.
    """
    for o in seccion["opciones"]:
        if o.get("grupo"):
            yield from o["hijas"]
        else:
            yield o


# =============================================================================
# Lectura de los menús de los módulos
# =============================================================================
@lru_cache(maxsize=1)
def estructura():
    """
    Lee el menu.py de cada módulo de settings.MODULOS_MENU y devuelve la lista
    completa de módulos, con sus 4 secciones, sus opciones (y grupos) y las
    direcciones web ya calculadas.

    @lru_cache: el menú no cambia mientras el sistema está corriendo, así que
    se calcula una sola vez (la primera visita) y luego se reutiliza.
    """
    modulos = []
    for nombre in settings.MODULOS_MENU:                       # en el orden de settings
        menu = import_module(f"{nombre}.menu").MENU            # lee <modulo>/menu.py
        url_modulo = reverse(f"{nombre}:inicio")               # p. ej. "/inventario/"
        secciones = []
        for seccion in SECCIONES:                              # las 4 secciones, en orden
            opciones = []
            for op in menu["opciones"].get(seccion["clave"], []):
                if op.get("grupo"):
                    # Grupo: se preparan sus sub-opciones (cada una con su dirección).
                    hijas = [_preparar(nombre, seccion["clave"], h, grupo=op) for h in op["hijas"]]
                    opciones.append({**op, "hijas": hijas})
                else:
                    opciones.append(_preparar(nombre, seccion["clave"], op))
            sec = {**seccion, "opciones": opciones,
                   "url": f"{url_modulo}#{seccion['clave']}"}   # ancla en la página del módulo
            sec["total"] = sum(1 for _o in hojas(sec))          # cantidad de opciones (sin contar grupos)
            secciones.append(sec)
        modulos.append({
            "nombre": nombre,                                  # nombre de la carpeta
            "titulo": menu["titulo"],                          # (textos con _(): se traducen al mostrarse)
            "descripcion": menu.get("descripcion", ""),
            "icono": menu.get("icono", nombre),
            "color": menu.get("color", "#2a3653"),
            "url": url_modulo,
            "secciones": secciones,
            "total": sum(s["total"] for s in secciones),       # cantidad de opciones
        })
    _resolver_compartidas(modulos)
    return modulos


def _preparar(modulo, seccion, op, grupo=None):
    """
    Completa una opción con su dirección web y si está pendiente.
    grupo -> el grupo al que pertenece (o None si está suelta); se guarda su
             título para mostrarlo en el buscador y en las migas de pan.
    """
    return {
        **op,                                              # clave, titulo, ayuda, compartida
        "url": _url_opcion(modulo, seccion, op, grupo),
        "pendiente": not op.get("url"),                    # True = sin pantalla todavía
        "grupo_clave": grupo["clave"] if grupo else None,
        "grupo_titulo": grupo["titulo"] if grupo else None,
    }


def _resolver_compartidas(modulos):
    """
    Segunda vuelta: las opciones "compartidas" toman la dirección y el estado
    (pendiente o no) de la opción dueña, que está en otro módulo. Se hace al
    final porque la dueña puede estar en un módulo que se leyó después.
    Además guarda en "duena" el título del módulo dueño (para mostrar
    "Compartida con Compras y Cuentas por Pagar").
    Si la opción dueña no existe (error al escribirla), se lanza un error claro
    al arrancar, en vez de dejar un enlace roto.
    """
    for m in modulos:
        for s in m["secciones"]:
            for o in hojas(s):
                if not o.get("compartida"):
                    continue
                partes = o["compartida"].split(":")              # "cxp:tablas:proveedores"
                mod, sec, clave = partes[0], partes[1], partes[-1]
                grupo_clave = partes[2] if len(partes) == 4 else None
                duena = next((x for dm in modulos if dm["nombre"] == mod
                              for ds in dm["secciones"] if ds["clave"] == sec
                              for x in hojas(ds)
                              if x["clave"] == clave and x["grupo_clave"] == grupo_clave), None)
                if duena is None:
                    raise ValueError(f"Opción compartida inexistente: {o['compartida']} "
                                     f"(en {m['nombre']}/menu.py, opción {o['clave']})")
                modulo_dueno = next(dm for dm in modulos if dm["nombre"] == mod)
                o["url"] = duena["url"]                              # misma pantalla
                o["pendiente"] = duena["pendiente"]
                o["duena"] = modulo_dueno["titulo"]


def _url_opcion(modulo, seccion, op, grupo=None):
    """
    Dirección web de una opción:
      - si tiene pantalla (url), la de esa pantalla;
      - si no, la de "Under construction":
            /<modulo>/<seccion>/<clave>/              (opción suelta)
            /<modulo>/<seccion>/<grupo>/<clave>/      (opción dentro de un grupo)
    """
    if op.get("url"):
        try:
            return reverse(op["url"])
        except NoReverseMatch:
            pass                       # ruta mal escrita: se trata como pendiente en vez de romper
    if grupo:
        return reverse(f"{modulo}:pendiente_grupo",
                       kwargs={"seccion": seccion, "grupo": grupo["clave"], "opcion": op["clave"]})
    return reverse(f"{modulo}:pendiente", kwargs={"seccion": seccion, "opcion": op["clave"]})


# =============================================================================
# Lo que usan las pantallas
# =============================================================================
def menu(usuario, ruta_actual=""):
    """
    Devuelve el menú para un usuario, marcando dónde está parado:
        modulo["activo"]   = True en el módulo de la pantalla actual
        seccion["activa"]  = True en la sección de la opción actual
        grupo["activa"]    = True en el grupo de la opción actual (queda abierto)
        opcion["activa"]   = True en la opción actual

    usuario     -> el usuario de la sesión (si no inició sesión, el menú queda vacío).
    ruta_actual -> request.path, la dirección de la pantalla actual.

    PERMISOS: cuando se definan, aquí se quitarán los módulos u opciones que
    el usuario no pueda ver.
    """
    if not usuario.is_authenticated:
        return []
    modulos = copy.deepcopy(estructura())          # copia: así marcar "activo" no altera el original
    for m in modulos:
        m["activo"] = ruta_actual.startswith(m["url"])
        for s in m["secciones"]:
            for o in hojas(s):
                o["activa"] = (o["url"] == ruta_actual)
            for o in s["opciones"]:
                if o.get("grupo"):
                    o["activa"] = any(h["activa"] for h in o["hijas"])
            s["activa"] = any(o["activa"] for o in s["opciones"])
    return modulos


def buscar_modulo(nombre):
    """Devuelve un módulo de la estructura por su nombre de carpeta, o None."""
    return next((m for m in estructura() if m["nombre"] == nombre), None)


def indice_busqueda(modulos):
    """
    Lista plana de todas las opciones, para el buscador de la barra superior
    (nucleo/static/nucleo/js/app.js). Va a la pantalla como JSON.
    Cada elemento: t = título, m = módulo, s = sección, u = dirección,
    p = pendiente, c = color del módulo, k = palabras extra para buscar.

    k lleva los nombres en TODOS los idiomas (inglés y español) y la clave de
    la opción, así se encuentra escribiendo en cualquiera de los dos, sin
    importar el idioma elegido en config.xml.
    """
    def en_todos(texto):
        """El texto traducido a cada idioma del sistema, unido con espacios."""
        partes = []
        for codigo, _nombre in settings.LANGUAGES:
            with translation.override(codigo):          # traduce temporalmente a ese idioma
                partes.append(str(texto))
        return " ".join(partes)

    return [
        {"t": str(o["titulo"]), "m": str(m["titulo"]),
         # s = la sección, y el grupo si la opción está dentro de uno ("Procesos › Conteo...")
         "s": str(s["titulo"]) + (f" › {o['grupo_titulo']}" if o["grupo_titulo"] else ""),
         "u": o["url"], "p": o["pendiente"], "c": m["color"],
         "k": " ".join([en_todos(o["titulo"]), en_todos(s["titulo"]), en_todos(m["titulo"]),
                        en_todos(o["grupo_titulo"]) if o["grupo_titulo"] else "",
                        o["clave"].replace("-", " ")])}
        for m in modulos for s in m["secciones"] for o in hojas(s)
    ]
