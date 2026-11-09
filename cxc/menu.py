"""
cxc/menu.py
===========

Opciones del módulo Ventas y Cuentas por Cobrar en el menú. Las lee nucleo/modulos.py.

Cada opción se crea con opcion(clave, titulo, url=None):
    clave   identificador corto, sin espacios (va en la dirección web:
            /cxc/<seccion>/<clave>/)
    titulo  lo que ve el usuario, en inglés dentro de _() (se traduce al
            idioma de config.xml con el django.po del módulo)
    url     nombre de la ruta de su pantalla. Mientras no se indique, la
            opción muestra "Under construction".

Para activar una opción cuando su pantalla esté hecha, por ejemplo:
    opcion("clientes", _("Customers"), url="cxc:clientes"),
Para agregar una opción: una línea más en la sección que corresponda, y su
traducción en locale/es/LC_MESSAGES/django.po (luego: python manage.py compilar_idiomas).
El orden de las líneas es el orden en el menú.
"""

# gettext_lazy como _: marca el texto para traducir. Los textos se escriben en
# inglés y su traducción al español está en <modulo>/locale/es/LC_MESSAGES/django.po
from django.utils.translation import gettext_lazy as _

from nucleo.modulos import opcion      # función que arma cada opción

MENU = {
    "titulo": _("Sales & Accounts Receivable"),       # nombre del módulo en pantalla
    # Texto debajo del nombre (en el tablero y en la página del módulo):
    # ventas, clientes, cobranza y saldos por cobrar.
    "descripcion": _("Sales, customers, collections and receivable balances."),
    "icono": "cxc",                           # dibujo en nucleo/static/nucleo/img/iconos.svg
    "color": "#15803d",                       # color propio del módulo (verde)
    "opciones": {
        # Tablas (Tables): datos maestros y catálogos.
        "tablas": [
            opcion("clientes", _("Customers")),
            opcion("tipos-cliente", _("Customer types")),
            opcion("zonas", _("Zones")),
            opcion("segmentos", _("Segments")),
            opcion("vendedores", _("Sales reps")),
            opcion("paises", _("Countries")),
            # Misma pantalla que en Inventario › Tablas (un solo programa, dos accesos):
            opcion("almacenes", _("Warehouses"), compartida="inventario:tablas:almacenes"),
            opcion("sucursales", _("Branches"), compartida="inventario:tablas:sucursales"),
            opcion("condiciones-pago", _("Payment terms")),
            opcion("transportes", _("Carriers")),
            opcion("puntos-tarjetas", _("POS terminals - Credit/Debit cards")),
            opcion("cuentas-ingreso-egreso", _("Income/Expense accounts")),
            opcion("descuentos", _("Discounts")),
            opcion("comisiones", _("Commissions")),
            opcion("moneda", _("Currency")),
            opcion("turnos-pos", _("Point of sale shifts")),
        ],
        # Procesos (Processes): operaciones del día a día.
        "procesos": [
            opcion("facturas", _("Sales invoices")),
            # En inglés se llaman "Packing List" y "Proforma"; en español, Pedidos y Cotizaciones a Clientes.
            opcion("pedidos", _("Packing List")),
            opcion("cotizaciones", _("Proforma")),
            opcion("devoluciones", _("Customer returns")),
            opcion("notas-entrega", _("Delivery notes")),
            opcion("plantillas-venta", _("Sales templates")),
            opcion("turnos", _("Open and close shifts")),
            opcion("documentos-venta", _("Sales documents")),
            opcion("cobranza", _("Collections")),
            opcion("giros", _("Generate bills of exchange")),
            opcion("empaques", _("Packing")),
            opcion("control-empaques", _("Packing control")),
        ],
        # Reportes (Reports): listados para imprimir o exportar.
        "reportes": [
            opcion("clientes", _("Customers")),
            opcion("vendedores", _("Sales reps")),
            opcion("facturas", _("Sales invoices")),
            opcion("pedidos", _("Packing List")),
            opcion("cotizaciones", _("Proforma")),
            opcion("devoluciones", _("Customer returns")),
            opcion("notas-entrega", _("Delivery notes")),
            opcion("notas-despacho", _("Dispatch notes")),
            opcion("plantillas-venta", _("Sales templates")),
            opcion("documentos-cxc", _("A/R documents")),
            opcion("punto-venta", _("Point of sale")),
            opcion("empaques", _("Packing")),
            opcion("cobranza", _("Collections")),
            opcion("tablas", _("Sales & A/R tables")),
            opcion("libro-ventas", _("Sales ledger")),
            opcion("estado-cuenta", _("Customer account statement")),
            opcion("vencimientos", _("Customer aging (overdue / not yet due)")),
            opcion("analisis-ventas", _("Sales analysis")),
            opcion("estadisticas-ventas", _("Sales statistics")),
            opcion("margen-ganancia", _("Sales profit margin")),
        ],
        # Consultas (Queries): consultas rápidas en pantalla.
        "consultas": [
            opcion("saldo-cliente", _("Customer balance")),
            opcion("documentos-pendientes", _("Open documents")),
            opcion("historial-cliente", _("Customer history")),
        ],
    },
}
