"""
iniciar.py
==========

Arranca el Sistema Administrativo con Waitress, el servidor web para producción en Windows.

    python iniciar.py

Escucha en la dirección y el puerto que indica config.xml
(<web><escuchar> y <web><puerto>). Se detiene con Ctrl+C.
Más adelante se instalará como servicio de Windows.
"""

import os

# Indica a Django qué archivo de configuración usar (antes de importar Django).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema.settings")

from django.conf import settings  # noqa: E402  (configuración ya cargada)
from waitress import serve  # noqa: E402       (el servidor web)

from sistema.wsgi import application  # noqa: E402  (el sistema en sí)

if __name__ == "__main__":
    host, puerto = settings.CFG["escuchar"], settings.CFG["puerto"]
    print(f"Sistema Administrativo en http://{host}:{puerto}   (Ctrl+C para detener)")
    serve(
        application,
        host=host,                      # IP donde escucha (127.0.0.1 = solo este servidor)
        port=puerto,                    # puerto
        threads=8,                      # atiende hasta 8 visitas a la vez
        trusted_proxy="127.0.0.1",      # confía en Cloudflare Tunnel / IIS del mismo servidor
        trusted_proxy_headers={"x-forwarded-proto"},   # ...para saber si la visita vino por https
    )
