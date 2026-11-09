"""
nucleo/apps.py
==============

Registro del módulo "nucleo" en Django.

El núcleo es la base común que usan todos los módulos:
    - las plantillas: base.html (lo mínimo), plantilla_acceso.html (login y
      empresa) y plantilla_app.html (barra superior + menú lateral),
    - el tablero de inicio, la página de cada módulo y "Under construction",
    - el armado del menú (nucleo/modulos.py) y sus rutas comunes (nucleo/rutas.py),
    - la conexión de solo lectura a Profit (nucleo/profit.py),
    - estilos, logo, íconos, escáner y JavaScript compartido (nucleo/static/nucleo/).

El núcleo no aparece en el menú (no tiene menu.py).
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _   # texto traducible


class NucleoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nucleo"                  # nombre de la carpeta
    verbose_name = _("Core")            # nombre que se muestra en el panel /admin/
