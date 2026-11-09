"""
cajas_bancos/urls.py
====================

Pantallas (páginas web) del módulo Cajas y Bancos.
sistema/urls.py las monta bajo /cajas-bancos/.

Hoy solo tiene las rutas comunes a todos los módulos (nucleo/rutas.py):
    /cajas-bancos/                       página del módulo con sus 4 secciones
    /cajas-bancos/<seccion>/<opcion>/    "Under construction"

Para agregar una pantalla propia:
    1. Crear su función en cajas_bancos/views.py.
    2. Agregar su path() en la lista de abajo, ANTES de rutas_basicas.
    3. Ponerle url="cajas_bancos:<nombre>" a su opción en cajas_bancos/menu.py.
"""

from nucleo.rutas import rutas_basicas     # rutas comunes a todos los módulos

# from . import views                      # (descomentar cuando haya pantallas propias)

# Espacio de nombres: las rutas se nombran "cajas_bancos:inicio", "cajas_bancos:pendiente", ...
app_name = "cajas_bancos"

urlpatterns = [
    # --- Pantallas propias del módulo (aquí arriba) ---
    # path("<seccion>/<clave>/", views.<funcion>, name="<nombre>"),

    # --- Rutas comunes (siempre al final) ---
    *rutas_basicas("cajas_bancos"),
]
