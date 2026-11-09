"""
cxp/urls.py
===========

Pantallas (páginas web) del módulo Compras y Cuentas por Pagar.
sistema/urls.py las monta bajo /cxp/.

Hoy solo tiene las rutas comunes a todos los módulos (nucleo/rutas.py):
    /cxp/                       página del módulo con sus 4 secciones
    /cxp/<seccion>/<opcion>/    "Under construction"

Para agregar una pantalla propia:
    1. Crear su función en cxp/views.py.
    2. Agregar su path() en la lista de abajo, ANTES de rutas_basicas.
    3. Ponerle url="cxp:<nombre>" a su opción en cxp/menu.py.
"""

from nucleo.rutas import rutas_basicas     # rutas comunes a todos los módulos

# from . import views                      # (descomentar cuando haya pantallas propias)

# Espacio de nombres: las rutas se nombran "cxp:inicio", "cxp:pendiente", ...
app_name = "cxp"

urlpatterns = [
    # --- Pantallas propias del módulo (aquí arriba) ---
    # path("<seccion>/<clave>/", views.<funcion>, name="<nombre>"),

    # --- Rutas comunes (siempre al final) ---
    *rutas_basicas("cxp"),
]
