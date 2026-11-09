"""
empresas/urls.py
================

Rutas del módulo empresas. Se enchufan en sistema/urls.py bajo "/empresa/".

    /empresa/    elegir (o cambiar) la empresa con la que se trabaja
"""

from django.urls import path

from . import views

app_name = "empresas"        # permite referirse a la ruta como "empresas:seleccionar"

urlpatterns = [
    path("", views.seleccionar, name="seleccionar"),
]
