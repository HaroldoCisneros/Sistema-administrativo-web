"""
cxc/urls.py
===========

Pantallas (páginas web) del módulo Ventas y Cuentas por Cobrar.
sistema/urls.py las monta bajo /cxc/.

Hoy solo tiene las rutas comunes a todos los módulos (nucleo/rutas.py):
    /cxc/                       página del módulo con sus 4 secciones
    /cxc/<seccion>/<opcion>/    "Under construction"

Para agregar una pantalla propia:
    1. Crear su función en cxc/views.py.
    2. Agregar su path() en la lista de abajo, ANTES de rutas_basicas.
    3. Ponerle url="cxc:<nombre>" a su opción en cxc/menu.py.
"""

from nucleo.rutas import rutas_basicas     # rutas comunes a todos los módulos

# from . import views                      # (descomentar cuando haya pantallas propias)

# Espacio de nombres: las rutas se nombran "cxc:inicio", "cxc:pendiente", ...
app_name = "cxc"

urlpatterns = [
    # --- Pantallas propias del módulo (aquí arriba) ---
    # path("<seccion>/<clave>/", views.<funcion>, name="<nombre>"),

    # --- Rutas comunes (siempre al final) ---
    *rutas_basicas("cxc"),
]
