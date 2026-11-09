"""
empresas/middleware.py
======================

Exige haber elegido una empresa antes de entrar a cualquier pantalla de trabajo.
Está activado en sistema/settings.py (MIDDLEWARE), después del de usuarios.

Qué hace en cada visita:
    1. Si el usuario NO ha iniciado sesión, no hace nada (de eso se encarga
       @login_required en cada pantalla, que lo manda al login).
    2. Si ya inició sesión, lee la empresa de la sesión y la deja en
       request.empresa (así cualquier pantalla sabe con qué empresa trabaja).
    3. Si todavía no eligió empresa y la pantalla NO es una de las libres
       (login, elegir empresa, panel /admin/), lo manda a elegir empresa y,
       después, lo regresa a donde iba (?next=...).
"""

from django.conf import settings
from django.contrib.auth.views import redirect_to_login   # arma la redirección con ?next=
from django.shortcuts import resolve_url                   # "empresas:seleccionar" -> "/empresa/"

from . import sesion


class EmpresaMiddleware:
    # Grupos de pantallas (app_name de sus urls.py) que se pueden usar sin empresa.
    LIBRES = {"cuentas", "empresas", "admin"}

    def __init__(self, get_response):
        """Django crea el middleware una sola vez al arrancar."""
        self.get_response = get_response               # la función que sigue en la cadena

    def __call__(self, request):
        """Se ejecuta en CADA visita, antes de saber qué pantalla se pidió."""
        request.empresa = None                         # por defecto, sin empresa
        return self.get_response(request)              # sigue con la visita normal

    def process_view(self, request, vista, args, kwargs):
        """
        Django lo llama justo antes de ejecutar la pantalla, cuando ya sabe
        cuál es (request.resolver_match). Si devuelve algo, esa respuesta
        reemplaza a la pantalla (aquí: la redirección a elegir empresa).
        """
        if not request.user.is_authenticated:          # paso 1
            return None
        request.empresa = sesion.leer(request)         # paso 2
        grupo = request.resolver_match.app_name if request.resolver_match else ""
        if request.empresa is None and grupo not in self.LIBRES:   # paso 3
            return redirect_to_login(request.get_full_path(), resolve_url(settings.EMPRESA_URL))
        return None                                    # None = seguir normalmente
