"""
sistema/settings.py
===================

Configuración general de Django. Django lee este archivo una sola vez al
arrancar. Los valores que cambian por instalación NO se escriben aquí: salen
de config.xml a través de sistema/configuracion.py.

Secciones de este archivo:
    1. Configuración leída de config.xml
    2. Módulos del sistema   <- aquí se agregan los módulos nuevos
    3. Middleware y plantillas
    4. Bases de datos
    5. Usuarios, inicio de sesión y empresa
    6. API
    7. Idioma, archivos estáticos y seguridad
    8. Registro de errores (log)
"""

from pathlib import Path                   # manejo de rutas de archivos

# gettext_lazy marca un texto para traducir; "lazy" (perezoso) significa que
# se traduce recién cuando se muestra, ya con el idioma activo.
from django.utils.translation import gettext_lazy as _

from . import configuracion                # nuestro lector de config.xml

# Carpeta raíz del proyecto (la que contiene manage.py).
# __file__ es este archivo; .parent.parent sube dos niveles: sistema/ -> raíz.
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# 1. Configuración leída de config.xml
# =============================================================================
CFG = configuracion.leer()                 # diccionario con todo el config.xml

SECRET_KEY = CFG["clave_secreta"]          # firma las sesiones (no compartir)
DEBUG = CFG["depuracion"]                  # True solo para desarrollo: muestra errores detallados
ALLOWED_HOSTS = CFG["dominios"]            # dominios por los que se permite entrar
# Nombre que se muestra en las pantallas. Si config.xml lo deja vacío, se usa
# el nombre por defecto traducido al idioma elegido.
NOMBRE_SISTEMA = CFG["nombre"] or _("Administrative System")
MARCA = CFG["marca"]                       # marca del sistema: SIGHEC


# =============================================================================
# 2. Módulos del sistema
# =============================================================================
# Cada módulo es una carpeta independiente con su propio código, pantallas,
# menú, estilos y pruebas.
#
# MODULOS_BASE: piezas internas que todos necesitan (no salen en el menú).
MODULOS_BASE = [
    "nucleo",          # base común: plantillas, diseño, menú, conexión a Profit
    "cuentas",         # inicio de sesión con los usuarios de Profit
    "empresas",        # selección de la empresa con la que se trabaja
]

# MODULOS_MENU: los módulos de trabajo. Salen en el menú EN ESTE ORDEN.
# Para AGREGAR un módulo nuevo:
#   1) crear su carpeta (copiando la estructura de "cxc", que es la más simple),
#   2) agregar su nombre aquí,
#   3) agregar su línea en sistema/urls.py.
MODULOS_MENU = [
    "inventario",      # Inventory
    "cxc",             # Sales & Accounts Receivable      (ventas y cuentas por cobrar)
    "cxp",             # Purchasing & Accounts Payable    (compras y cuentas por pagar)
    "cajas_bancos",    # Cash & Banks         (cajas y bancos)
    "mantenimiento",   # Maintenance          (mantenimiento)
]

# Todos nuestros módulos juntos (los usa el registro de errores, más abajo).
MODULOS = MODULOS_BASE + MODULOS_MENU

INSTALLED_APPS = [
    # Nuestros módulos van PRIMERO: cuando un mismo texto tiene traducción en
    # Django y en un módulo nuestro, gana la del que está más arriba en esta
    # lista (así "Username" se traduce "Usuario" y no "Nombre de usuario").
    *MODULOS,
    # Aplicaciones que trae Django:
    "django.contrib.admin",          # panel de administración (/admin/)
    "django.contrib.auth",           # usuarios, grupos y permisos
    "django.contrib.contenttypes",   # necesaria para permisos
    "django.contrib.sessions",       # sesiones (recordar quién inició sesión)
    "django.contrib.messages",       # mensajes entre pantallas
    "django.contrib.staticfiles",    # archivos estáticos (css, js, imágenes)
    "rest_framework",                # Django REST Framework: la API
]


# =============================================================================
# 3. Middleware y plantillas
# =============================================================================
# El middleware son "filtros" por los que pasa cada visita, en este orden.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",          # cabeceras de seguridad
    "whitenoise.middleware.WhiteNoiseMiddleware",              # sirve css/js/imágenes
    "django.contrib.sessions.middleware.SessionMiddleware",    # maneja la sesión
    "django.middleware.common.CommonMiddleware",               # ajustes comunes de URL
    "django.middleware.csrf.CsrfViewMiddleware",               # protege los formularios
    "django.contrib.auth.middleware.AuthenticationMiddleware", # identifica al usuario
    "django.contrib.messages.middleware.MessageMiddleware",    # mensajes
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # impide incrustar la página
    # El nuestro: exige haber elegido empresa (va DESPUÉS del de usuario,
    # porque primero hay que saber quién es).
    "empresas.middleware.EmpresaMiddleware",
]

ROOT_URLCONF = "sistema.urls"              # archivo con todas las rutas
WSGI_APPLICATION = "sistema.wsgi.application"   # punto de entrada para Waitress

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],                  # no hay carpeta global: cada módulo trae sus plantillas
        "APP_DIRS": True,            # busca en <modulo>/templates/
        "OPTIONS": {
            # Datos que quedan disponibles en TODAS las pantallas:
            "context_processors": [
                "django.template.context_processors.request",          # {{ request }}
                "django.contrib.auth.context_processors.auth",         # {{ user }}
                "django.contrib.messages.context_processors.messages", # {{ messages }}
                "nucleo.context_processors.sistema",                   # nombre, menú y empresa
            ],
        },
    },
]


# =============================================================================
# 4. Bases de datos (todas en el mismo SQL Server)
# =============================================================================
#   default  -> base propia del sistema (usuarios, sesiones, empresas, ...)
#   usuarios -> base donde están los usuarios de Profit (hoy MasterProfit). SOLO LECTURA.
#
# La base de Profit de CADA EMPRESA no se declara aquí: se conecta sola al
# elegir la empresa (ver nucleo/profit.py, función conexion_empresa).
def conexion(nombre_base):
    """Arma la configuración de conexión de Django para una base de datos."""
    sql = CFG["sql"]
    return {
        "ENGINE": "mssql",                       # paquete mssql-django (SQL Server)
        "NAME": nombre_base,                     # nombre de la base
        "HOST": sql["servidor"],                 # servidor (y la instancia, si tiene)
        "USER": sql["usuario"],                  # usuario de SQL
        "PASSWORD": sql["clave"],                # clave de ese usuario
        "OPTIONS": {
            "driver": sql["driver"],             # driver ODBC instalado en el servidor
            # El Driver 18 exige un certificado válido; en una red interna no suele
            # haberlo, así que se confía en el certificado del servidor SQL.
            "extra_params": "TrustServerCertificate=yes",
        },
        "CONN_MAX_AGE": 60,                      # reutiliza la conexión 60 s (más rápido)
        "CONN_HEALTH_CHECKS": True,              # verifica que la conexión siga viva
    }


DATABASES = {
    "default": conexion(CFG["base_sistema"]),
    "usuarios": conexion(CFG["usuarios"]["base"]),
}

# Reglas que impiden que Django cree o modifique tablas en las bases de Profit.
DATABASE_ROUTERS = ["sistema.rutas_bd.RutasBD"]

# Tipo de las claves primarias de las tablas propias del sistema.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# 5. Usuarios, inicio de sesión y empresa
# =============================================================================
USUARIOS = CFG["usuarios"]                 # origen, base, tabla, mayúsculas

if USUARIOS["origen"] == "profit":
    # Primero se valida contra la tabla de usuarios de Profit.
    # El segundo permite entrar a administradores creados en el propio sistema
    # (python manage.py createsuperuser).
    AUTHENTICATION_BACKENDS = [
        "cuentas.backends.ProfitBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]
else:
    # Usuarios propios del sistema (cuando nos independicemos de Profit).
    AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

INTENTOS_LOGIN = CFG["intentos_login"]     # fallos seguidos antes de bloquear 15 minutos
LOGIN_URL = "cuentas:entrar"               # a dónde se manda a quien no ha iniciado sesión
LOGIN_REDIRECT_URL = "nucleo:inicio"       # a dónde va después de iniciar sesión
LOGOUT_REDIRECT_URL = "cuentas:entrar"     # a dónde va después de cerrar sesión
# Después del login, el middleware de empresas (empresas/middleware.py) ve que
# todavía no hay empresa elegida y lo lleva a esta pantalla:
EMPRESA_URL = "empresas:seleccionar"

SESSION_COOKIE_AGE = 8 * 60 * 60           # la sesión dura 8 horas
SESSION_EXPIRE_AT_BROWSER_CLOSE = False    # sigue abierta aunque cierre el navegador

# Solo aplica a usuarios propios del sistema (no a los de Profit).
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

# Memoria temporal (se usa para contar los intentos fallidos de inicio de sesión).
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


# =============================================================================
# 6. API (Django REST Framework)
# =============================================================================
REST_FRAMEWORK = {
    # La API reconoce al usuario por su sesión iniciada en el navegador.
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Toda función de la API exige sesión iniciada, salvo que se diga lo contrario.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    # Las respuestas siempre son JSON.
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    # Límite de consultas por usuario, para evitar abusos: 300 por minuto.
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.UserRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"user": "300/min"},
}


# =============================================================================
# 7. Idioma, archivos estáticos y seguridad
# =============================================================================
# Idioma de las pantallas: sale de config.xml (<web><idioma>): "es" o "en".
# Los textos se escriben en INGLÉS en el código y en las plantillas, marcados
# para traducir:
#     en Python:     _("Customers")                 (gettext / gettext_lazy)
#     en plantillas: {% translate "Customers" %}
# y su traducción al español está en el archivo de cada módulo:
#     <modulo>/locale/es/LC_MESSAGES/django.po
# Si config.xml dice "en", se muestran tal cual; si dice "es", Django busca
# la traducción. Django encuentra solo la carpeta locale/ de cada módulo.
LANGUAGE_CODE = CFG["idioma"]
LANGUAGES = list(configuracion.IDIOMAS.items())   # idiomas disponibles
USE_I18N = True                            # activa las traducciones
TIME_ZONE = "America/Caracas"              # hora de Venezuela
USE_TZ = True                              # guarda las fechas con zona horaria

STATIC_URL = "static/"                     # dirección web de los archivos estáticos
# Cada módulo trae sus archivos en <modulo>/static/<modulo>/...
# "collectstatic" los junta todos en esta carpeta para servirlos:
STATIC_ROOT = BASE_DIR / "archivos_estaticos"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    # Comprime los archivos y les agrega una huella en el nombre, para que el
    # navegador descargue la versión nueva cada vez que se actualice el sistema.
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

if CFG["https"]:
    # Publicado en internet detrás de Cloudflare / IIS, que manejan el https.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # confía en el aviso del proxy
    SESSION_COOKIE_SECURE = True           # la sesión solo viaja por https
    CSRF_COOKIE_SECURE = True              # la protección de formularios solo por https
    CSRF_TRUSTED_ORIGINS = [f"https://{d}" for d in ALLOWED_HOSTS
                            if d not in ("localhost", "127.0.0.1")]
SESSION_COOKIE_HTTPONLY = True             # JavaScript no puede leer la cookie de sesión
X_FRAME_OPTIONS = "DENY"                   # nadie puede meter el sistema dentro de otra página
SECURE_CONTENT_TYPE_NOSNIFF = True         # el navegador no "adivina" el tipo de archivo
SECURE_REFERRER_POLICY = "same-origin"     # no se envía la dirección a otros sitios


# =============================================================================
# 8. Registro de errores (log)
# =============================================================================
# Todo error o aviso queda en sighec.log (junto a manage.py).
# Cuando el archivo llega a 5 MB se renombra (.1, .2, .3) y se empieza uno nuevo.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "{asctime}  {levelname}  {name}  {message}", "style": "{"}},
    "handlers": {
        "archivo": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "sighec.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {"handlers": ["archivo"], "level": "WARNING"},   # errores de Django
        # Cada módulo escribe con su propio nombre, para saber de dónde vino el error:
        **{modulo: {"handlers": ["archivo"], "level": "INFO"} for modulo in MODULOS},
    },
}
