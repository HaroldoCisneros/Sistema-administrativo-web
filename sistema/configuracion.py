"""
sistema/configuracion.py
========================

Lee el archivo config.xml (que está junto a manage.py) y devuelve todos sus
valores en un diccionario de Python.

¿Por qué existe este archivo?
    Todo lo que cambia de una instalación a otra (idioma, nombre del sistema, servidor
    de SQL, claves, base propia, dominio, de dónde salen los usuarios...)
    vive en config.xml. Así, para instalar el sistema en otro servidor, o el
    día que dejemos de depender de Profit, basta con editar el XML: no hay
    que tocar el código.

¿Quién lo usa?
    Solo sistema/settings.py, que lo llama una vez al arrancar el sistema.
"""

# --- Librerías estándar de Python -----------------------------------------
import re                        # expresiones regulares (para validar nombres)
import secrets                   # genera textos aleatorios seguros (clave secreta)
from pathlib import Path         # manejo de rutas de archivos
import xml.etree.ElementTree as ET   # lector de archivos XML

# --- Django ----------------------------------------------------------------
# ImproperlyConfigured es el error que Django muestra cuando la configuración
# está mal; lo usamos para que los mensajes sean claros al arrancar.
from django.core.exceptions import ImproperlyConfigured

# CARPETA = carpeta raíz del proyecto (la que contiene manage.py).
# __file__ es este archivo; .parent.parent sube dos niveles: sistema/ -> raíz.
CARPETA = Path(__file__).resolve().parent.parent

# Ruta del archivo de configuración.
RUTA_CONFIG = CARPETA / "config.xml"

# Archivo donde se guarda la clave secreta de Django (se crea solo).
# La clave secreta firma las sesiones de los usuarios: NO se debe compartir.
RUTA_CLAVE_SECRETA = CARPETA / "clave_secreta.txt"

# Idiomas que tiene el sistema: código -> nombre. Para agregar otro idioma
# (por ejemplo portugués, "pt"), se agrega aquí y se crean sus archivos de
# traducción (ver LEEME.txt, "IDIOMAS").
IDIOMAS = {"es": "Español", "en": "English"}

# Patrón permitido para nombres de bases de datos y tablas: solo letras,
# números y guion bajo. Esos nombres se escriben dentro de consultas SQL,
# así que validarlos evita que un valor raro en el XML rompa (o altere) el SQL.
_NOMBRE_VALIDO = re.compile(r"^[A-Za-z0-9_]+$")


def _texto(raiz, xpath, defecto=""):
    """
    Devuelve el texto de una etiqueta del XML.

    raiz    -> el XML ya leído.
    xpath   -> la ruta de la etiqueta, por ejemplo "sqlserver/servidor".
    defecto -> lo que se devuelve si la etiqueta no existe o está vacía.
    """
    nodo = raiz.find(xpath)                                  # busca la etiqueta
    texto = (nodo.text or "").strip() if nodo is not None else ""  # su texto sin espacios
    return texto or defecto                                  # si está vacío, el valor por defecto


def _si(valor):
    """Convierte 'si', 'sí', 's', 'yes', 'true' o '1' en True; cualquier otra cosa en False."""
    return valor.strip().lower() in ("si", "sí", "s", "yes", "true", "1")


def nombre_valido(valor, etiqueta):
    """
    Valida un nombre de base de datos o de tabla.
    (También la usa el módulo empresas para validar la base de Profit de cada empresa.)
    Si está vacío o tiene caracteres no permitidos, detiene el arranque con un
    mensaje que dice exactamente qué etiqueta del XML hay que corregir.
    """
    if not valor:
        raise ImproperlyConfigured(f"config.xml: falta el valor de <{etiqueta}>")
    if not _NOMBRE_VALIDO.match(valor):
        raise ImproperlyConfigured(
            f"config.xml: <{etiqueta}> solo puede tener letras, números y _ (valor: {valor!r})")
    return valor


def _clave_secreta():
    """
    Devuelve la clave secreta de Django.
    La primera vez que arranca el sistema no existe: se genera una aleatoria
    y se guarda en clave_secreta.txt para usarla siempre la misma.
    (Si cambia, todos los usuarios tienen que volver a iniciar sesión.)
    """
    if RUTA_CLAVE_SECRETA.exists():
        return RUTA_CLAVE_SECRETA.read_text(encoding="utf-8").strip()
    clave = secrets.token_urlsafe(50)                        # 50 bytes aleatorios en texto
    RUTA_CLAVE_SECRETA.write_text(clave, encoding="utf-8")
    return clave


def leer(ruta=RUTA_CONFIG):
    """
    Lee config.xml completo y devuelve un diccionario con todos los valores,
    ya validados y convertidos al tipo correcto (números, sí/no, listas).
    """
    # 1) El archivo debe existir y ser un XML válido.
    if not ruta.exists():
        raise ImproperlyConfigured(f"No se encontró el archivo de configuración: {ruta}")
    try:
        raiz = ET.parse(ruta).getroot()
    except ET.ParseError as e:
        raise ImproperlyConfigured(f"config.xml tiene un error de formato: {e}")

    # 2) Dominios: vienen separados por coma -> se convierten en lista.
    dominios = [d.strip() for d in _texto(raiz, "web/dominios", "localhost").split(",")
                if d.strip()]

    # 3) Origen de los usuarios: 'profit' (MasterProfit) o 'sistema' (propios).
    origen = _texto(raiz, "usuarios/origen", "profit").lower()
    if origen not in ("profit", "sistema"):
        raise ImproperlyConfigured("config.xml: <usuarios/origen> debe ser 'profit' o 'sistema'")

    # 4) Idioma de las pantallas: 'es' (español) o 'en' (inglés).
    idioma = _texto(raiz, "web/idioma", "es").lower()
    if idioma not in IDIOMAS:
        raise ImproperlyConfigured(
            f"config.xml: <web/idioma> debe ser uno de: {', '.join(IDIOMAS)} (valor: {idioma!r})")

    # 5) Valores numéricos.
    try:
        puerto = int(_texto(raiz, "web/puerto", "8010"))
        intentos = int(_texto(raiz, "web/intentos_login", "5"))
    except ValueError:
        raise ImproperlyConfigured("config.xml: <web/puerto> e <web/intentos_login> deben ser números")

    # 6) Se arma el diccionario final que usará settings.py.
    return {
        "clave_secreta": _clave_secreta(),
        "idioma": idioma,                                                 # es / en
        "nombre": _texto(raiz, "web/nombre"),                            # vacío = según el idioma
        "marca": _texto(raiz, "web/marca", "SIGHEC"),                     # marca del sistema
        "depuracion": _si(_texto(raiz, "web/depuracion", "no")),     # modo de desarrollo
        "dominios": dominios,                                         # dominios permitidos
        "escuchar": _texto(raiz, "web/escuchar", "127.0.0.1"),        # IP donde escucha Waitress
        "puerto": puerto,                                             # puerto de Waitress
        "https": _si(_texto(raiz, "web/https", "si")),                # ¿publicado con https?
        "intentos_login": intentos,                                   # fallos antes de bloquear
        "sql": {                                                      # conexión a SQL Server
            "servidor": _texto(raiz, "sqlserver/servidor"),
            "usuario": _texto(raiz, "sqlserver/usuario"),
            "clave": _texto(raiz, "sqlserver/clave"),
            "driver": _texto(raiz, "sqlserver/driver", "ODBC Driver 18 for SQL Server"),
        },
        # Base propia del sistema (usuarios, sesiones, empresas y lo que se agregue).
        # La base de Profit de cada empresa NO va aquí: se guarda en la tabla de
        # empresas (módulo empresas), porque cada empresa tiene la suya.
        "base_sistema": nombre_valido(_texto(raiz, "bases/sistema", "SIGHEC"),
                                "bases/sistema"),
        "usuarios": {
            "origen": origen,
            "base": nombre_valido(_texto(raiz, "usuarios/base", "MasterProfit"), "usuarios/base"),
            "tabla": nombre_valido(_texto(raiz, "usuarios/tabla", "employee"), "usuarios/tabla"),
            "clave_mayusculas": _si(_texto(raiz, "usuarios/clave_mayusculas", "no")),
        },
    }
