"""
sistema/settings_prueba.py
==========================

Configuración SOLO para las pruebas automáticas. No necesita SQL Server:
reemplaza las bases por bases temporales en memoria (SQLite).

Uso:
    python manage.py test --settings=sistema.settings_prueba
"""

from .settings import *  # noqa: F401,F403  (toma toda la configuración normal...)

# ...y cambia solo lo necesario para probar sin SQL Server:
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
    "usuarios": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
}
# Cifrado de claves rápido (solo para que las pruebas corran rápido).
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
# Archivos estáticos sin compresión (no hace falta collectstatic para probar).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
# Las pruebas se escriben con los textos en inglés (las de español fijan "es" aparte).
LANGUAGE_CODE = "en"
# Durante las pruebas no se escribe el archivo de log.
LOGGING = {"version": 1, "disable_existing_loggers": False}
