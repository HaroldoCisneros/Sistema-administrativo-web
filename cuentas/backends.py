"""
cuentas/backends.py
===================

Inicio de sesión contra la tabla de usuarios de Profit (MasterProfit.dbo.employee).

Un "backend de autenticación" es la pieza que Django consulta para decidir
si un usuario y una clave son correctos. Está activado en sistema/settings.py
(AUTHENTICATION_BACKENDS) cuando config.xml dice <origen>profit</origen>.

Qué hace, paso a paso, cuando alguien intenta entrar:
    1. Pasa el usuario a mayúsculas (así se guardan en Profit).
    2. Si ese usuario o esa IP tienen demasiados intentos fallidos, lo rechaza
       por 15 minutos (protege contra quien prueba claves al azar).
    3. Lee el usuario en la tabla employee de Profit.
    4. Verifica que esté activo, con Estado = 'A', y que la clave coincida
       (con la misma encriptación de Profit, ver cuentas/encriptacion.py).
    5. Si todo está bien, crea o actualiza un usuario "espejo" en la base
       propia del sistema. Ese espejo NO tiene clave (la clave siempre se
       valida en Profit) y es el que se usará para asignar permisos.

Para independizarse de Profit: poner <origen>sistema</origen> en config.xml;
entonces se usan usuarios propios del sistema y este archivo deja de usarse.
"""

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.cache import cache

from nucleo.profit import consultar         # acceso de solo lectura a Profit (núcleo)

from .encriptacion import clave_coincide

# Registro de eventos: queda en sighec.log con el nombre "cuentas".
log = logging.getLogger("cuentas")

MINUTOS_BLOQUEO = 15       # tiempo de bloqueo tras demasiados intentos fallidos


# =============================================================================
# Bloqueo por intentos fallidos
# =============================================================================
# Los intentos se cuentan en la memoria temporal (CACHES en settings.py):
#   - por usuario: se bloquea al llegar a INTENTOS_LOGIN (config.xml, 5 por defecto)
#   - por IP:      se bloquea al llegar a 4 veces ese número (alguien probando
#                  muchos usuarios distintos desde el mismo equipo)
def _clave_intentos(tipo, valor):
    """Nombre con el que se guarda el contador en la memoria temporal."""
    return f"login_fallos:{tipo}:{valor}"


def esta_bloqueado(usuario, ip):
    limite = settings.INTENTOS_LOGIN
    return (cache.get(_clave_intentos("u", usuario), 0) >= limite
            or cache.get(_clave_intentos("ip", ip), 0) >= limite * 4)


def registrar_fallo(usuario, ip):
    """Suma 1 a los contadores del usuario y de la IP (duran 15 minutos)."""
    for tipo, valor in (("u", usuario), ("ip", ip)):
        clave = _clave_intentos(tipo, valor)
        cache.add(clave, 0, MINUTOS_BLOQUEO * 60)     # lo crea en 0 si no existía
        try:
            cache.incr(clave)                          # le suma 1
        except ValueError:                             # venció justo en este instante
            cache.set(clave, 1, MINUTOS_BLOQUEO * 60)


def limpiar_fallos(usuario):
    """Al entrar bien, se borra el contador del usuario."""
    cache.delete(_clave_intentos("u", usuario))


def ip_de(request):
    """
    IP real de quien se conecta. Detrás de Cloudflare, la IP del visitante
    viene en la cabecera CF-Connecting-IP; detrás de otro proxy, en
    X-Forwarded-For; si no hay proxy, en REMOTE_ADDR.
    """
    if request is None:
        return "-"
    reenviada = request.META.get("HTTP_CF_CONNECTING_IP") or \
        request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    return reenviada or request.META.get("REMOTE_ADDR", "-")


# =============================================================================
# Lectura del usuario en Profit
# =============================================================================
def leer_empleado(codigo):
    """
    Busca el usuario en la tabla de usuarios de Profit.
    Devuelve un diccionario con sus datos, o None si no existe.

    La clave se lee con CAST(... AS VARBINARY) para obtener los bytes exactos,
    sin que SQL Server los convierta a texto.
    """
    # Nombre de la tabla: sale de config.xml y ya se validó que solo tenga
    # letras, números y _ (sistema/configuracion.py), por eso puede ir en el SQL.
    tabla = settings.USUARIOS["tabla"]
    filas = consultar(
        f"SELECT employee_i, last_name, CAST(password AS VARBINARY(15)) AS clave, activo, Estado "
        f"FROM [dbo].[{tabla}] WHERE employee_i = %s",
        [codigo],
        base="usuarios",                 # la base MasterProfit (config.xml <usuarios><base>)
    )
    if not filas:
        return None
    fila = filas[0]
    return {
        "codigo": (fila["employee_i"] or "").strip(),
        "nombre": (fila["last_name"] or "").strip(),
        "clave": fila["clave"],
        "activo": bool(fila["activo"]),
        "estado": (fila["estado"] or "").strip().upper(),
    }


# =============================================================================
# El backend
# =============================================================================
class ProfitBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Django llama a esta función al enviar el formulario de inicio de sesión.
        Devuelve el usuario si los datos son correctos, o None si no.
        """
        if not username or not password:
            return None
        codigo = username.strip().upper()          # en Profit los usuarios van en mayúsculas
        ip = ip_de(request)

        # Paso 2: ¿bloqueado por intentos fallidos?
        if esta_bloqueado(codigo, ip):
            log.warning("Login bloqueado por intentos fallidos: usuario=%s ip=%s", codigo, ip)
            if request is not None:
                # Marca para que el formulario muestre el mensaje de bloqueo.
                request.login_bloqueado = True
            return None

        # Paso 3: leer el usuario en Profit.
        try:
            empleado = leer_empleado(codigo)
        except Exception:
            # Error de conexión u otro: queda en el log con todo el detalle.
            log.exception("No se pudo leer la tabla de usuarios de Profit")
            return None

        # Paso 4: activo, Estado 'A' y clave correcta.
        valido = (
            empleado is not None
            and empleado["activo"]
            and empleado["estado"] == "A"
            and clave_coincide(password, empleado["clave"],
                               settings.USUARIOS["clave_mayusculas"])
        )
        if not valido:
            registrar_fallo(codigo, ip)
            log.info("Login fallido: usuario=%s ip=%s", codigo, ip)
            return None

        # Paso 5: usuario espejo en la base propia del sistema.
        limpiar_fallos(codigo)
        Usuario = get_user_model()
        usuario, nuevo = Usuario.objects.get_or_create(username=codigo)
        if nuevo:
            usuario.set_unusable_password()        # sin clave propia: siempre se valida en Profit
        usuario.first_name = empleado["nombre"][:150]   # nombre que se muestra en la barra
        usuario.is_active = True
        usuario.save()
        log.info("Login correcto: usuario=%s ip=%s", codigo, ip)
        return usuario

    def get_user(self, user_id):
        """Django llama a esta función en cada visita para recuperar al usuario de la sesión."""
        Usuario = get_user_model()
        return Usuario.objects.filter(pk=user_id, is_active=True).first()
