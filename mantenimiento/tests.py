"""
mantenimiento/tests.py
======================

Pruebas automáticas del módulo Mantenimiento (no necesitan SQL Server):
    python manage.py test mantenimiento --settings=sistema.settings_prueba

Las pruebas comunes a todos los módulos (el menú tiene las 4 secciones, la
página del módulo abre, las opciones llevan a "Under construction", ...)
están en nucleo/pruebas.py; aquí solo se indica qué módulo probar.
Las pruebas propias de cada pantalla se agregan debajo.
"""

# Se importa el archivo (no la clase) para que Django no corra la clase base sola.
from nucleo import pruebas


class MenuTests(pruebas.PruebasModulo):
    modulo = "mantenimiento"          # carpeta del módulo que se prueba
