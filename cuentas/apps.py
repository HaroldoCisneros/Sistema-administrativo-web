"""
cuentas/apps.py
===============

Registro del módulo "cuentas": inicio y cierre de sesión.

Hoy los usuarios entran con su usuario y clave de Profit
(MasterProfit.dbo.employee). La lógica está en cuentas/backends.py.

Este módulo no tiene opción en el menú (no declara "menu"): su pantalla
es la de inicio de sesión, que aparece sola cuando hace falta.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _   # texto traducible


class CuentasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cuentas"
    verbose_name = _("User accounts")
