"""
inventario/urls.py
==================

Pantallas (páginas web) del módulo Inventario.
sistema/urls.py las monta bajo /inventario/.

Hoy solo tiene las rutas comunes a todos los módulos (nucleo/rutas.py):
    /inventario/                       página del módulo con sus 4 secciones
    /inventario/<seccion>/<opcion>/    "Under construction"

Para agregar una pantalla propia:
    1. Crear su función en inventario/views.py.
    2. Agregar su path() en la lista de abajo, ANTES de rutas_basicas.
    3. Ponerle url="inventario:<nombre>" a su opción en inventario/menu.py.
"""

from nucleo.rutas import rutas_basicas     # rutas comunes a todos los módulos

# from . import views                      # (descomentar cuando haya pantallas propias)

# Espacio de nombres: las rutas se nombran "inventario:inicio", "inventario:pendiente", ...
app_name = "inventario"

urlpatterns = [
    # --- Pantallas propias del módulo (aquí arriba) ---
    # path("<seccion>/<clave>/", views.<funcion>, name="<nombre>"),

    # --- Rutas comunes (siempre al final) ---
    *rutas_basicas("inventario"),
]
