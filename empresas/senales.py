"""
empresas/senales.py
===================

"Señales": funciones que Django ejecuta solas cuando pasa algo.

user_logged_in se dispara cada vez que alguien inicia sesión. En ese momento
se olvida la empresa que pudiera quedar en la sesión, para que el sistema
SIEMPRE pida la empresa después del login (paso 2).

Se conecta en empresas/apps.py (método ready).
"""

from django.contrib.auth.signals import user_logged_in    # la señal de "inició sesión"
from django.dispatch import receiver                      # conecta una función a una señal

from . import sesion


@receiver(user_logged_in)
def pedir_empresa_al_entrar(sender, request, user, **kwargs):
    """Al iniciar sesión, borra la empresa de la sesión."""
    if request is not None:                    # (al iniciar sesión desde una prueba puede no haber request)
        sesion.olvidar(request)
