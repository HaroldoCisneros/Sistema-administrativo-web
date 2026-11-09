"""
cuentas/urls.py
===============

Rutas del módulo cuentas. Se enchufan en sistema/urls.py bajo "/cuentas/".

    /cuentas/entrar/   pantalla de inicio de sesión
    /cuentas/salir/    cierra la sesión (se llama con POST desde el botón "Sign out")

Se usan las vistas estándar de Django (LoginView y LogoutView), que ya
manejan la sesión de forma segura; solo se les indica el formulario y la plantilla.
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import FormularioEntrada

app_name = "cuentas"         # permite referirse a las rutas como "cuentas:entrar"

urlpatterns = [
    path("entrar/", auth_views.LoginView.as_view(
        template_name="cuentas/login.html",        # nuestra pantalla
        authentication_form=FormularioEntrada,      # nuestro formulario
        redirect_authenticated_user=True,           # si ya inició sesión, no le muestra el login
    ), name="entrar"),
    path("salir/", auth_views.LogoutView.as_view(), name="salir"),
]
