"""
cuentas/forms.py
================

Formulario de la pantalla de inicio de sesión.

Se basa en el formulario estándar de Django (AuthenticationForm), que ya
se encarga de validar con los backends de autenticación. Aquí solo se
cambian los textos y se agrega el mensaje de "demasiados intentos".
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
# gettext_lazy como _: textos en inglés que se traducen al idioma de config.xml
# (traducción en cuentas/locale/es/LC_MESSAGES/django.po).
from django.utils.translation import gettext_lazy as _


class FormularioEntrada(AuthenticationForm):
    # Campo "usuario": se enfoca solo al abrir la pantalla, y en el teléfono
    # sugiere escribir en mayúsculas y no corrige la ortografía.
    username = forms.CharField(
        label=_("Username"), max_length=30,
        widget=forms.TextInput(attrs={"autofocus": True, "autocapitalize": "characters",
                                      "autocomplete": "username", "spellcheck": "false",
                                      "placeholder": _("Your Profit user")}))
    # Campo "clave": strip=False para no quitar espacios que formen parte de la clave.
    password = forms.CharField(
        label=_("Password"), strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          "placeholder": "••••••••"}))

    # Mensajes de error. Por seguridad no se dice si falló el usuario o la clave.
    error_messages = {
        "invalid_login": _("Incorrect username or password."),
        "inactive": _("This user is inactive."),
    }

    def clean(self):
        """
        Valida el formulario. Si el backend marcó el intento como bloqueado
        (cuentas/backends.py), se muestra ese mensaje en lugar del genérico.
        """
        try:
            return super().clean()
        except forms.ValidationError:
            if getattr(self.request, "login_bloqueado", False):
                raise forms.ValidationError(
                    _("Too many failed attempts. Please wait 15 minutes and try again."),
                    code="bloqueado")
            raise
