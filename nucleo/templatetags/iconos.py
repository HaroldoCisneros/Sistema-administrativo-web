"""
nucleo/templatetags/iconos.py
=============================

Etiqueta {% icono %} para dibujar los íconos del sistema en las plantillas.

Todos los íconos están en UN solo archivo: nucleo/static/nucleo/img/iconos.svg
(cada uno es un <symbol id="i-NOMBRE">). El navegador lo descarga una vez y
lo reutiliza en todas las pantallas.

Uso en una plantilla:
    {% load iconos %}
    {% icono "inventario" %}                 ->  ícono de inventario
    {% icono "buscar" "icono--grande" %}     ->  con una clase de estilo extra

Para agregar un ícono nuevo: agregar su <symbol id="i-nuevo"> en iconos.svg.
"""

from django import template
from django.templatetags.static import static     # dirección web de un archivo estático
from django.utils.html import format_html         # arma HTML escapando los valores

register = template.Library()                     # registro de etiquetas de este archivo


@register.simple_tag
def icono(nombre, clase=""):
    """
    Devuelve el <svg> que muestra el ícono "nombre".
    aria-hidden: los lectores de pantalla lo ignoran (es solo decorativo).
    """
    return format_html(
        '<svg class="icono {}" aria-hidden="true" focusable="false">'
        '<use href="{}#i-{}"></use></svg>',
        clase,                                    # clase extra (opcional)
        static("nucleo/img/iconos.svg"),          # archivo con todos los íconos
        nombre,                                   # cuál de ellos
    )
