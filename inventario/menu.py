"""
inventario/menu.py
==================

Opciones del módulo Inventario en el menú. Las lee nucleo/modulos.py.

Cada opción se crea con opcion(clave, titulo, url=None):
    clave   identificador corto, sin espacios (va en la dirección web:
            /inventario/<seccion>/<clave>/)
    titulo  lo que ve el usuario, en inglés dentro de _() (se traduce al
            idioma de config.xml con el django.po del módulo)
    url     nombre de la ruta de su pantalla. Mientras no se indique, la
            opción muestra "Under construction".

Para activar una opción cuando su pantalla esté hecha, por ejemplo:
    opcion("articulos", _("Items"), url="inventario:articulos"),
Para agregar una opción: una línea más en la sección que corresponda, y su
traducción en locale/es/LC_MESSAGES/django.po (luego: python manage.py compilar_idiomas).
El orden de las líneas es el orden en el menú.
"""

# gettext_lazy como _: marca el texto para traducir. Los textos se escriben en
# inglés y su traducción al español está en <modulo>/locale/es/LC_MESSAGES/django.po
from django.utils.translation import gettext_lazy as _

from nucleo.modulos import grupo, opcion   # funciones que arman cada opción y cada grupo

MENU = {
    "titulo": _("Inventory"),                 # nombre del módulo en pantalla
    # Texto debajo del nombre (en el tablero y en la página del módulo):
    # artículos, almacenes, movimientos de existencia y conteos físicos.
    "descripcion": _("Items, warehouses, stock movements and physical counts."),
    "icono": "inventario",                    # dibujo en nucleo/static/nucleo/img/iconos.svg
    "color": "#0f766e",                       # color propio del módulo (verde azulado)
    "opciones": {
        # Tablas (Tables): datos maestros y catálogos.
        "tablas": [
            opcion("articulos", _("Items")),
            opcion("articulos-compuestos", _("Composite items")),
            opcion("lineas", _("Item lines")),
            opcion("categorias", _("Item categories")),
            opcion("sublineas", _("Sub-lines")),
            opcion("procedencias", _("Origins")),
            opcion("colores", _("Colors")),
            opcion("unidades", _("Units")),
            opcion("sucursales", _("Branches")),
            opcion("almacenes", _("Warehouses")),
            opcion("tipos-ajuste", _("Adjustment types")),
            # Misma pantalla que Compras y Cuentas por Pagar › Tablas › Proveedores (un solo programa):
            opcion("proveedores", _("Suppliers"), compartida="cxp:tablas:proveedores"),
        ],
        # Procesos (Processes): operaciones del día a día.
        "procesos": [
            opcion("ajustes", _("Inventory adjustments")),
            opcion("traslados", _("Inventory transfers between warehouses")),
            # grupo(): opción con sub-opciones (en el menú se abre como una carpeta)
            grupo("conteo-fisico", _("Physical inventory count"), [
                opcion("preparar-cerrar", _("Prepare and close count")),
                opcion("ingresar-resultados", _("Enter count results")),
            ]),
            grupo("ajuste-precios", _("Price adjustment"), [
                opcion("automatico", _("Automatic")),
                opcion("manual", _("Manual")),
            ]),
            opcion("generacion-compuestos", _("Composite items generation")),
        ],
        # Reportes (Reports): listados para imprimir o exportar.
        "reportes": [
            opcion("articulos", _("Items")),
            opcion("ajustes", _("Inbound and outbound adjustments")),
            opcion("traslados", _("Transfers between warehouses")),
            opcion("inventario-fisico", _("Physical inventory")),
            opcion("movimientos", _("Inventory movements")),
            opcion("tablas", _("Inventory tables")),
            opcion("compuestos-generados", _("Generated composite items")),
        ],
        # Consultas (Queries): consultas rápidas en pantalla.
        "consultas": [
            opcion("ficha-articulo", _("Price Product Info")),   # la ficha que ya existe en la app de consulta; se integrará aquí
            opcion("existencia-articulo", _("Item stock")),
            opcion("movimientos-articulo", _("Item movements")),
            opcion("ubicaciones-articulo", _("Item locations")),
        ],
    },
}
