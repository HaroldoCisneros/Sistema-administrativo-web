"""
sistema/wsgi.py
===============

Punto de entrada que usa el servidor web (Waitress, desde iniciar.py) para
hacer funcionar el sistema. No hace falta modificarlo.
"""

import os

from django.core.wsgi import get_wsgi_application

# Indica a Django qué archivo de configuración usar.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema.settings")

# "application" es lo que Waitress ejecuta con cada visita.
application = get_wsgi_application()
