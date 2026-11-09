"""
empresas/admin.py
=================

Muestra la tabla de empresas en el panel de administración de Django
(/admin/), para crearlas, editarlas o desactivarlas mientras no exista la
pantalla propia (Maintenance › Tables › Companies).
"""

from django.contrib import admin

from .models import Empresa


@admin.register(Empresa)              # registra la tabla en el panel
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "rif", "base_profit", "activa")   # columnas de la lista
    list_filter = ("activa",)                                              # filtro a la derecha
    search_fields = ("codigo", "nombre", "rif")                            # buscador
