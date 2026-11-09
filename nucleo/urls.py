"""
nucleo/urls.py
==============

Rutas del núcleo. Se enchufan en sistema/urls.py bajo "/".

    /   -> tablero de inicio

(Las páginas de cada módulo y "Under construction" las crea nucleo/rutas.py
dentro de las rutas de cada módulo.)
"""

from django.urls import path

from . import views

app_name = "nucleo"          # permite referirse a las rutas como "nucleo:inicio"

urlpatterns = [
    path("", views.inicio, name="inicio"),
]
