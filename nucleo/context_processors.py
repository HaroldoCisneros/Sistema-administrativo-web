"""
nucleo/context_processors.py
============================

Un "context processor" agrega datos a TODAS las pantallas automáticamente.
Está activado en sistema/settings.py (TEMPLATES > context_processors).

Deja disponibles en cualquier plantilla:
    {{ nombre_sistema }}   nombre del sistema (config.xml <web><nombre>)
    {{ marca }}            nombre de la empresa dueña (config.xml <web><marca>)
    {{ menu_modulos }}     módulos, secciones y opciones (ver nucleo/modulos.py)
    {{ indice_menu }}      las mismas opciones en una lista plana, para el buscador
    {{ empresa }}          la empresa con la que se está trabajando (o None)
    {{ modulos_sistema }}  los módulos instalados, aunque no haya sesión
                           (solo para mostrar sus nombres en la pantalla de acceso)
    {{ textos_js }}        textos que muestra JavaScript, ya traducidos
                           (base.html los deja en la página; comun.js los lee
                           con Sistema.t("clave"))
"""

from django.conf import settings
from django.utils.translation import gettext_lazy as _    # texto traducible

from . import modulos

# Textos de JavaScript. Para agregar uno: una línea aquí, su traducción en
# nucleo/locale/es/LC_MESSAGES/django.po, y en JavaScript se usa Sistema.t("clave").
# {texto} es un marcador que JavaScript reemplaza (por ejemplo, lo que se buscó).
TEXTOS_JS = {
    "sin_resultados": _("No options match “{texto}”"),
    "pronto": _("Soon"),
    "sin_conexion": _("No connection with the server."),
    "sesion_vencida": _("Session expired."),
    "error": _("Error {codigo}"),
    "camara_https": _("The camera only works when the page is opened with https://"),
    "camara_error": _("Could not open the camera. Check that the browser is allowed to use it."),
}


def sistema(request):
    # El menú del usuario, marcando la pantalla en la que está.
    menu = modulos.menu(request.user, request.path)
    return {
        "nombre_sistema": settings.NOMBRE_SISTEMA,
        "marca": settings.MARCA,
        "menu_modulos": menu,
        "indice_menu": modulos.indice_busqueda(menu),
        # request.empresa lo pone empresas/middleware.py. getattr(..., None)
        # evita un error en pantallas donde el middleware no actuó (errores 404, etc.).
        "empresa": getattr(request, "empresa", None),
        "modulos_sistema": modulos.estructura(),
        "textos_js": TEXTOS_JS,
    }
