"""
nucleo/views.py
===============

Pantallas comunes del núcleo:

    inicio          tablero que se ve después de elegir la empresa
    pagina_modulo   página de un módulo con sus 4 secciones (Tables, Processes,
                    Reports, Queries) y las opciones de cada una
    pendiente       "Under construction" para las opciones que aún no tienen pantalla

Ninguna necesita traer datos propios: el menú ({{ menu_modulos }}) y la
empresa ({{ empresa }}) ya llegan a todas las pantallas por
nucleo/context_processors.py.
"""

from django.contrib.auth.decorators import login_required   # exige sesión iniciada
from django.http import Http404                             # error "no existe"
from django.shortcuts import render                         # dibuja una plantilla
from django.utils import timezone                           # fecha y hora de Venezuela

from . import modulos                                       # el menú del sistema


# @login_required: si no ha iniciado sesión, lo manda a la pantalla de login
# (settings.LOGIN_URL) y, al entrar, regresa aquí. La empresa la exige el
# middleware de empresas (empresas/middleware.py) antes de llegar aquí.
@login_required
def inicio(request):
    """Tablero de inicio: saludo, datos de la sesión y un recuadro por módulo."""
    # ahora: fecha y hora local (settings.TIME_ZONE), para la fecha y el
    # saludo "Good morning / afternoon / evening".
    return render(request, "nucleo/inicio.html", {"ahora": timezone.localtime()})


@login_required
def pagina_modulo(request, modulo):
    """
    Página de un módulo. "modulo" llega desde nucleo/rutas.py (por ejemplo
    "inventario"). Se busca en el menú ya marcado para este usuario, para
    respetar los permisos cuando existan.
    """
    datos = _buscar(request, modulo)
    return render(request, "nucleo/modulo.html", {"modulo": datos})


@login_required
def pendiente(request, modulo, seccion, opcion, grupo=None):
    """
    "Under construction": se muestra al entrar a una opción del menú que
    todavía no tiene pantalla. grupo llega solo si la opción está dentro de un
    grupo (/inventario/procesos/conteo-fisico/preparar-cerrar/).
    Si la sección, el grupo o la opción no existen en el menú del módulo
    (dirección escrita a mano), responde "no existe" (404).
    """
    datos = _buscar(request, modulo)
    # next(...) devuelve el primero que cumpla la condición, o None si ninguno.
    sec = next((s for s in datos["secciones"] if s["clave"] == seccion), None)
    if sec is None:
        raise Http404("Section not found")
    if grupo:
        # Buscar el grupo y, dentro de él, la opción.
        gru = next((o for o in sec["opciones"] if o.get("grupo") and o["clave"] == grupo), None)
        lista = gru["hijas"] if gru else []
    else:
        gru = None
        lista = [o for o in sec["opciones"] if not o.get("grupo")]
    op = next((o for o in lista if o["clave"] == opcion), None)
    if op is None:
        raise Http404("Option not found")
    return render(request, "nucleo/pendiente.html",
                  {"modulo": datos, "seccion": sec, "grupo": gru, "opcion": op})


def _buscar(request, nombre):
    """Busca un módulo en el menú del usuario; si no está, responde 404."""
    for m in modulos.menu(request.user, request.path):
        if m["nombre"] == nombre:
            return m
    raise Http404("Module not found")
