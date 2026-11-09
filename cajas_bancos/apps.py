"""
cajas_bancos/apps.py
====================

Registro del módulo "cajas_bancos" (Cajas y Bancos) en Django.

Archivos del módulo:
    apps.py      este archivo (registro)
    menu.py      opciones del módulo en el menú (Tables, Processes, Reports, Queries)
    urls.py      direcciones de sus pantallas  (/cajas-bancos/...)
    views.py     sus pantallas propias (por ahora ninguna: usa las comunes del núcleo)
    tests.py     pruebas automáticas

Cuando se programen pantallas, se agregan además (igual que en la app de consulta):
    servicios.py                  consultas a la base de datos
    api.py / urls_api.py          su API  (/api/v1/cajas-bancos/...)
    templates/cajas_bancos/            HTML de sus pantallas
    static/cajas_bancos/css|js/        estilos y JavaScript propios
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _   # texto traducible


class CajasBancosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cajas_bancos"                    # nombre de la carpeta
    verbose_name = _("Cash & Banks")      # nombre en el panel /admin/
