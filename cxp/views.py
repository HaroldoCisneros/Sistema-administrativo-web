"""
cxp/views.py
============

Pantallas propias del módulo Compras y Cuentas por Pagar.

Todavía no tiene: la página del módulo y "Under construction" son comunes a
todos y están en nucleo/views.py. Aquí irán las pantallas de cada opción.

Modelo de una pantalla (exige sesión; la empresa elegida está en request.empresa):

    from django.contrib.auth.decorators import login_required
    from django.shortcuts import render

    @login_required
    def mi_pantalla(request):
        return render(request, "cxp/mi_pantalla.html")

y su plantilla empieza con:  {% extends "nucleo/plantilla_app.html" %}
"""
