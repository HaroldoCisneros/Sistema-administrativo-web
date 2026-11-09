"""
cxp/menu.py
===========

Opciones del módulo Compras y Cuentas por Pagar en el menú. Las lee nucleo/modulos.py.

Cada opción se crea con opcion(clave, titulo, url=None):
    clave   identificador corto, sin espacios (va en la dirección web:
            /cxp/<seccion>/<clave>/)
    titulo  lo que ve el usuario, en inglés dentro de _() (se traduce al
            idioma de config.xml con el django.po del módulo)
    url     nombre de la ruta de su pantalla. Mientras no se indique, la
            opción muestra "Under construction".

Para activar una opción cuando su pantalla esté hecha, por ejemplo:
    opcion("proveedores", _("Suppliers"), url="cxp:proveedores"),
Para agregar una opción: una línea más en la sección que corresponda, y su
traducción en locale/es/LC_MESSAGES/django.po (luego: python manage.py compilar_idiomas).
El orden de las líneas es el orden en el menú.
"""

# gettext_lazy como _: marca el texto para traducir. Los textos se escriben en
# inglés y su traducción al español está en <modulo>/locale/es/LC_MESSAGES/django.po
from django.utils.translation import gettext_lazy as _

from nucleo.modulos import grupo, opcion   # funciones que arman cada opción y cada grupo

MENU = {
    "titulo": _("Purchasing & Accounts Payable"),          # nombre del módulo en pantalla
    # Texto debajo del nombre (en el tablero y en la página del módulo):
    # compras, proveedores, pagos y saldos por pagar.
    "descripcion": _("Purchases, suppliers, payments and payable balances."),
    "icono": "cxp",                           # dibujo en nucleo/static/nucleo/img/iconos.svg
    "color": "#c2410c",                       # color propio del módulo (naranja)
    "opciones": {
        # Tablas (Tables): datos maestros y catálogos.
        "tablas": [
            opcion("proveedores", _("Suppliers")),
            opcion("tipos-proveedor", _("Supplier types")),
            # Tablas comunes con Ventas y Cuentas por Cobrar (la misma pantalla y los
            # mismos datos para clientes y proveedores, como en Profit):
            opcion("zonas", _("Zones"), compartida="cxc:tablas:zonas"),
            opcion("segmentos", _("Segments"), compartida="cxc:tablas:segmentos"),
            opcion("condiciones-pago", _("Payment terms"), compartida="cxc:tablas:condiciones-pago"),
            opcion("cuentas-ingreso-egreso", _("Income/Expense accounts"),
                   compartida="cxc:tablas:cuentas-ingreso-egreso"),
            opcion("convenios", _("Agreements")),
        ],
        # Procesos (Processes): operaciones del día a día.
        "procesos": [
            opcion("facturas-compra", _("Purchase invoices")),
            opcion("ordenes-compra", _("Purchase orders")),
            opcion("cotizaciones", _("Supplier quotes")),
            opcion("devoluciones", _("Returns to suppliers")),
            opcion("notas-recepcion", _("Receiving notes")),
            opcion("plantillas-compra", _("Purchase templates")),
            opcion("importaciones", _("Imports")),
            # grupo(): opción con sub-opciones (en el menú se abre como una carpeta)
            grupo("control-importaciones", _("Import control"), [
                opcion("distribucion-costos", _("Cost distribution")),
                opcion("expediente", _("Import file")),
            ]),
            opcion("documentos", _("Documents")),
            opcion("programacion-pagos", _("Payment scheduling")),
            opcion("pagos", _("Supplier payments")),
            # Giros a proveedores (distinto de Generar Giros de Ventas, que es a clientes):
            opcion("giros", _("Generate bills of exchange")),
        ],
        # Reportes (Reports): listados para imprimir o exportar.
        "reportes": [
            opcion("proveedores", _("Suppliers")),
            opcion("facturas-compra", _("Purchase invoices")),
            opcion("ordenes-compra", _("Purchase orders")),
            opcion("cotizaciones", _("Supplier quotes")),
            opcion("devoluciones", _("Returns to suppliers")),
            opcion("notas-recepcion", _("Receiving notes")),
            opcion("plantillas-compra", _("Purchase templates")),
            opcion("importaciones", _("Imports")),
            opcion("distribucion-costos", _("Cost distribution")),
            opcion("documentos-cxp", _("A/P documents")),
            opcion("pagos-autorizados", _("Authorized payments")),
            opcion("pagos", _("Payments")),
            opcion("cheques-emitidos", _("Issued checks format")),
            opcion("tablas", _("Purchasing & A/P tables")),
            opcion("libro-compras", _("Purchase ledger")),
            opcion("estado-cuenta", _("Supplier account statement")),
            opcion("vencimientos", _("Supplier aging (overdue / not yet due)")),
            opcion("analisis-compras", _("Purchase analysis")),
            opcion("estadisticas-compras", _("Purchase statistics")),
        ],
        # Consultas (Queries): consultas rápidas en pantalla.
        "consultas": [
            opcion("saldo-proveedor", _("Supplier balance")),
            opcion("documentos-pendientes", _("Open documents")),
            opcion("historial-proveedor", _("Supplier history")),
        ],
    },
}
