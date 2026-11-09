"""
empresas/forms.py
=================

Formulario de la pantalla "Elegir empresa" (Choose company): un solo campo, el código.

Valida que la empresa exista, esté activa y que el usuario tenga acceso
(empresas/acceso.py). Si todo está bien, deja la empresa en form.empresa
para que la vista la guarde en la sesión.
"""

from django import forms
# gettext_lazy como _: textos en inglés que se traducen al idioma de config.xml
# (traducción en empresas/locale/es/LC_MESSAGES/django.po).
from django.utils.translation import gettext_lazy as _

from .acceso import buscar_empresa


class FormularioEmpresa(forms.Form):
    # Campo del código. En el teléfono sugiere mayúsculas y no corrige la ortografía.
    codigo = forms.CharField(
        label=_("Company code"), max_length=10,
        widget=forms.TextInput(attrs={
            "autofocus": True,                     # el cursor empieza aquí
            "autocapitalize": "characters",        # teclado en mayúsculas (teléfono)
            "autocomplete": "off",                 # el navegador no sugiere valores viejos
            "spellcheck": "false",                 # sin corrector
            "placeholder": _("e.g. CF01"),         # ejemplo dentro del campo
        }))

    def __init__(self, *args, usuario=None, **kwargs):
        """
        Se crea el formulario recordando el usuario, porque la validación
        depende de qué empresas puede usar.
        """
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        self.empresa = None                        # se llena al validar

    def clean_codigo(self):
        """
        Django llama a clean_<campo>() al validar ese campo.
        Devuelve el código limpio o lanza un error con el mensaje a mostrar.
        """
        codigo = self.cleaned_data["codigo"].strip().upper()
        self.empresa = buscar_empresa(self.usuario, codigo)
        if self.empresa is None:
            # Por seguridad, el mismo mensaje si no existe, si está inactiva o si no tiene acceso.
            raise forms.ValidationError(
                _("That company code doesn't exist or isn't available to you."), code="no_existe")
        return codigo
