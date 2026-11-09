"""
nucleo/templatetags/formato.py
==============================

Filtros de formato para las plantillas.

Uso:
    {% load formato %}
    {{ "HAROLDO CISNEROS"|iniciales }}    ->  "HC"
    {{ hora|saludo }}                      ->  "Buenos días" / "Buenas tardes" / "Buenas noches"
                                               (o en inglés, según config.xml)
"""

from django import template
from django.utils.translation import gettext as _     # traduce al idioma activo

register = template.Library()          # registro de filtros de este archivo


@register.filter
def iniciales(nombre):
    """
    Iniciales de un nombre (máximo 2 letras), para el círculo del usuario.
    "HAROLDO CISNEROS" -> "HC";  "HCIS" -> "HC" (si es una sola palabra, sus 2 primeras letras).
    """
    palabras = str(nombre or "").split()              # separa por espacios
    if not palabras:
        return "?"
    if len(palabras) == 1:
        return palabras[0][:2].upper()                # una palabra: sus 2 primeras letras
    return (palabras[0][0] + palabras[1][0]).upper()  # dos o más: primera letra de las 2 primeras


@register.filter
def saludo(momento):
    """
    Saludo según la hora del día (momento = fecha y hora, por ejemplo now).
    Antes de las 12: mañana; antes de las 19: tarde; después: noche.
    """
    hora = momento.hour
    if hora < 12:
        return _("Good morning")
    if hora < 19:
        return _("Good afternoon")
    return _("Good evening")
