"""
mantenimiento/urls.py
=====================

Pantallas (páginas web) del módulo Mantenimiento.
sistema/urls.py las monta bajo /mantenimiento/.

Hoy solo tiene las rutas comunes a todos los módulos (nucleo/rutas.py):
    /mantenimiento/                       página del módulo con sus 4 secciones
    /mantenimiento/<seccion>/<opcion>/    "Under construction"

Para agregar una pantalla propia:
    1. Crear su función en mantenimiento/views.py.
    2. Agregar su path() en la lista de abajo, ANTES de rutas_basicas.
    3. Ponerle url="mantenimiento:<nombre>" a su opción en mantenimiento/menu.py.
"""

from nucleo.rutas import rutas_basicas     # rutas comunes a todos los módulos

# from . import views                      # (descomentar cuando haya pantallas propias)

# Espacio de nombres: las rutas se nombran "mantenimiento:inicio", "mantenimiento:pendiente", ...
app_name = "mantenimiento"

urlpatterns = [
    # --- Pantallas propias del módulo (aquí arriba) ---
    # path("<seccion>/<clave>/", views.<funcion>, name="<nombre>"),

    # --- Rutas comunes (siempre al final) ---
    *rutas_basicas("mantenimiento"),
]
