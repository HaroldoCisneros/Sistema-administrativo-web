"""
empresas/apps.py
================

Registro del módulo "empresas": la empresa con la que se trabaja.

Después de iniciar sesión, el sistema pide el código de la empresa
(pantalla /empresa/). Cada empresa tiene su propia base de datos en Profit,
y todo lo que se consulte o se haga en los módulos es sobre esa empresa.

Archivos del módulo:
    apps.py          este archivo (registro)
    models.py        la tabla de empresas (en la base propia del sistema)
    acceso.py        qué empresas puede usar cada usuario
    sesion.py        guardar / leer / olvidar la empresa en la sesión
    middleware.py    exige haber elegido empresa antes de entrar a los módulos
    senales.py       al iniciar sesión, olvida la empresa anterior (se pide de nuevo)
    forms.py         formulario del código de empresa
    views.py         pantalla para elegir la empresa
    urls.py          su dirección (/empresa/)
    admin.py         la tabla de empresas en el panel /admin/
    management/commands/crear_empresa.py   comando para dar de alta empresas
    templates/empresas/seleccionar.html    HTML de la pantalla
    tests.py         pruebas automáticas

Este módulo no tiene opción en el menú (no tiene menu.py).
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _   # texto traducible


class EmpresasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "empresas"                  # nombre de la carpeta
    verbose_name = _("Companies")         # nombre en el panel /admin/

    def ready(self):
        """
        Django llama a ready() una vez, cuando ya cargó todos los módulos.
        Aquí se conectan las "señales" (avisos automáticos) del módulo.
        El import se hace aquí adentro (y no arriba) porque las señales usan
        cosas de Django que todavía no están listas al cargar este archivo.
        """
        from . import senales  # noqa: F401  (basta con importarlo para que se conecte)
