"""
empresas/sesion.py
==================

Guarda, lee y olvida la empresa elegida en la SESIÓN del usuario.

La sesión es la "memoria" que Django guarda para cada navegador conectado
(en la tabla django_session de la base propia). Ahí se guarda solo el
CÓDIGO de la empresa; los demás datos se leen de la tabla de empresas en
cada visita, así un cambio (por ejemplo, desactivarla) se nota enseguida.
"""

from .acceso import buscar_empresa

# Nombre con el que se guarda el código en la sesión.
CLAVE = "empresa_codigo"


def guardar(request, empresa):
    """Guarda en la sesión la empresa elegida."""
    request.session[CLAVE] = empresa.codigo


def leer(request):
    """
    Devuelve la empresa guardada en la sesión, o None si:
      - todavía no eligió ninguna,
      - la empresa fue desactivada o borrada, o
      - el usuario ya no tiene acceso a ella.
    """
    codigo = request.session.get(CLAVE)               # .get: None si no existe
    if not codigo:
        return None
    return buscar_empresa(request.user, codigo)


def olvidar(request):
    """Borra la empresa de la sesión (el sistema la volverá a pedir)."""
    request.session.pop(CLAVE, None)                  # pop con None: no da error si no estaba
