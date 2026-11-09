"""
mantenimiento/menu.py
=====================

Opciones del módulo Mantenimiento en el menú. Las lee nucleo/modulos.py.

Cada opción se crea con opcion(clave, titulo, url=None):
    clave   identificador corto, sin espacios (va en la dirección web:
            /mantenimiento/<seccion>/<clave>/)
    titulo  lo que ve el usuario, en inglés dentro de _() (se traduce al
            idioma de config.xml con el django.po del módulo)
    url     nombre de la ruta de su pantalla. Mientras no se indique, la
            opción muestra "Under construction".

Para activar una opción cuando su pantalla esté hecha, por ejemplo:
    opcion("empresas", _("Companies"), url="mantenimiento:empresas"),
Para agregar una opción: una línea más en la sección que corresponda, y su
traducción en locale/es/LC_MESSAGES/django.po (luego: python manage.py compilar_idiomas).
El orden de las líneas es el orden en el menú.
"""

# gettext_lazy como _: marca el texto para traducir. Los textos se escriben en
# inglés y su traducción al español está en <modulo>/locale/es/LC_MESSAGES/django.po
from django.utils.translation import gettext_lazy as _

from nucleo.modulos import opcion      # función que arma cada opción

MENU = {
    "titulo": _("Maintenance"),               # nombre del módulo en pantalla
    # Texto debajo del nombre (en el tablero y en la página del módulo):
    # empresas, usuarios, permisos y configuración del sistema.
    "descripcion": _("Companies, users, permissions and system settings."),
    "icono": "mantenimiento",                 # dibujo en nucleo/static/nucleo/img/iconos.svg
    "color": "#6d28d9",                       # color propio del módulo (violeta)
    "opciones": {
        # Tablas (Tables): datos maestros y catálogos.
        "tablas": [
            opcion("empresas", _("Companies")),   # mientras tanto: panel /admin/ o python manage.py crear_empresa
            opcion("usuarios", _("Users")),
            opcion("perfiles", _("Roles")),
            opcion("permisos", _("Permissions")),
            opcion("impuestos", _("Taxes")),
            opcion("correlativos", _("Document numbering")),
        ],
        # Procesos (Processes): operaciones del día a día.
        "procesos": [
            opcion("usuarios-empresas", _("Assign users to companies")),
            opcion("importar-profit", _("Import data from Profit")),
            opcion("cierre-periodo", _("Period closing")),
        ],
        # Reportes (Reports): listados para imprimir o exportar.
        "reportes": [
            opcion("lista-usuarios", _("User list")),
            opcion("accesos", _("Access log")),
            opcion("auditoria", _("Audit trail")),
        ],
        # Consultas (Queries): consultas rápidas en pantalla.
        "consultas": [
            opcion("sesiones", _("Active sessions")),
            opcion("eventos", _("Event log")),
        ],
    },
}
