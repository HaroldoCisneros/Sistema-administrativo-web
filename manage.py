#!/usr/bin/env python
"""
manage.py
=========

Herramienta de Django para tareas de administración. Se usa desde la CMD,
dentro de la carpeta del proyecto. Los comandos que usaremos:

    python manage.py migrate                    crea/actualiza las tablas propias
    python manage.py collectstatic --noinput    junta css, js e imágenes
    python manage.py createsuperuser            crea un administrador propio
    python manage.py probar_usuario CODIGO      prueba la clave de un usuario de Profit
    python manage.py crear_empresa CF01 "Nombre" BASE_PROFIT   da de alta una empresa
    python manage.py compilar_idiomas           compila las traducciones (.po -> .mo)
    python manage.py test --settings=sistema.settings_prueba   pruebas automáticas
"""

import os
import sys


def main():
    # Indica a Django qué archivo de configuración usar.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema.settings")
    from django.core.management import execute_from_command_line
    # Ejecuta el comando que se escribió después de "python manage.py".
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
