"""
empresas/acceso.py
==================

Qué empresas puede usar cada usuario.

Hoy cualquier usuario que inició sesión puede trabajar con TODAS las
empresas activas. Cuando se definan los permisos (Maintenance), la regla se
cambia solo aquí, y la pantalla de elegir empresa y el middleware la
respetan sin tocar nada más.
"""

from .models import Empresa


def empresas_del_usuario(usuario):
    """
    Devuelve las empresas que el usuario puede elegir (consulta de Django,
    ordenada por código). Solo las activas.
    """
    return Empresa.objects.filter(activa=True)


def buscar_empresa(usuario, codigo):
    """
    Busca una empresa por su código entre las que el usuario puede usar.
    Devuelve la empresa, o None si no existe, está inactiva o no tiene acceso.
    """
    codigo = (codigo or "").strip().upper()            # los códigos se guardan en mayúsculas
    if not codigo:
        return None
    # .first(): la primera que cumpla, o None si ninguna.
    return empresas_del_usuario(usuario).filter(codigo=codigo).first()
