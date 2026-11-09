"""
cxc/apps.py
===========

Registro del módulo "cxc" (Ventas y Cuentas por Cobrar) en Django.

Archivos del módulo:
    apps.py      este archivo (registro)
    menu.py      opciones del módulo en el menú (Tables, Processes, Reports, Queries)
    urls.py      direcciones de sus pantallas  (/cxc/...)
    views.py     sus pantallas propias (por ahora ninguna: usa las comunes del núcleo)
    tests.py     pruebas automáticas

Cuando se programen pantallas, se agregan además (igual que en la app de consulta):
    servicios.py                  consultas a la base de datos
    api.py / urls_api.py          su API  (/api/v1/cxc/...)
    templates/cxc/            HTML de sus pantallas
    static/cxc/css|js/        estilos y JavaScript propios
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _   # texto traducible


class CxcConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cxc"                    # nombre de la carpeta
    verbose_name = _("Sales & Accounts Receivable")      # nombre en el panel /admin/
