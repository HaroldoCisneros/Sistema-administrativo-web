"""
sistema/urls.py
===============

Todas las direcciones (URL) del sistema. Cada módulo tiene su propio archivo
de rutas; aquí solo se "enchufa" cada uno bajo su prefijo.

Para agregar un módulo nuevo, sume una línea siguiendo el mismo patrón:
    path("<prefijo>/", include("<modulo>.urls")),
(y, cuando tenga API: path("api/v1/<prefijo>/", include("<modulo>.urls_api")),)
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # --- Piezas base ------------------------------------------------------
    path("", include("nucleo.urls")),                      # /  inicio (tablero)
    path("cuentas/", include("cuentas.urls")),             # /cuentas/entrar/  /cuentas/salir/
    path("empresa/", include("empresas.urls")),            # /empresa/  elegir empresa

    # --- Módulos de trabajo (el orden del menú lo da settings.MODULOS_MENU) --
    path("inventario/", include("inventario.urls")),       # Inventory
    path("cxc/", include("cxc.urls")),                     # Sales & Accounts Receivable
    path("cxp/", include("cxp.urls")),                     # Purchasing & Accounts Payable
    path("cajas-bancos/", include("cajas_bancos.urls")),   # Cash & Banks
    path("mantenimiento/", include("mantenimiento.urls")), # Maintenance

    # --- Panel de administración de Django (solo administradores) ----------
    path("admin/", admin.site.urls),
]
