"""
cajas_bancos/menu.py
====================

Opciones del módulo Cajas y Bancos en el menú. Las lee nucleo/modulos.py.

Cada opción se crea con opcion(clave, titulo, url=None):
    clave   identificador corto, sin espacios (va en la dirección web:
            /cajas-bancos/<seccion>/<clave>/)
    titulo  lo que ve el usuario, en inglés dentro de _() (se traduce al
            idioma de config.xml con el django.po del módulo)
    url     nombre de la ruta de su pantalla. Mientras no se indique, la
            opción muestra "Under construction".

Para activar una opción cuando su pantalla esté hecha, por ejemplo:
    opcion("cajas", _("Cash registers"), url="cajas_bancos:cajas"),
Para agregar una opción: una línea más en la sección que corresponda, y su
traducción en locale/es/LC_MESSAGES/django.po (luego: python manage.py compilar_idiomas).
El orden de las líneas es el orden en el menú.
"""

# gettext_lazy como _: marca el texto para traducir. Los textos se escriben en
# inglés y su traducción al español está en <modulo>/locale/es/LC_MESSAGES/django.po
from django.utils.translation import gettext_lazy as _

from nucleo.modulos import opcion      # función que arma cada opción

MENU = {
    "titulo": _("Cash & Banks"),              # nombre del módulo en pantalla
    # Texto debajo del nombre (en el tablero y en la página del módulo):
    # cajas, cuentas bancarias, transferencias y conciliación.
    "descripcion": _("Cash registers, bank accounts, transfers and reconciliation."),
    "icono": "cajas_bancos",                  # dibujo en nucleo/static/nucleo/img/iconos.svg
    "color": "#1d4ed8",                       # color propio del módulo (azul)
    "opciones": {
        # Tablas (Tables): datos maestros y catálogos.
        "tablas": [
            opcion("cuentas-bancarias", _("Bank accounts")),
            opcion("chequeras", _("Checkbooks")),
            opcion("cajas", _("Cash registers")),
            opcion("bancos", _("Banks")),
            opcion("beneficiarios", _("Payees")),
            # Tablas comunes con Ventas y Cuentas por Cobrar (la misma pantalla y los mismos datos):
            opcion("cuentas-ingreso-egreso", _("Income/Expense accounts"),
                   compartida="cxc:tablas:cuentas-ingreso-egreso"),
            opcion("tarjetas", _("Credit/Debit cards"), compartida="cxc:tablas:puntos-tarjetas"),
        ],
        # Procesos (Processes): operaciones del día a día.
        "procesos": [
            opcion("movimientos-caja", _("Cash movements")),
            opcion("movimientos-banco", _("Bank movements")),
            opcion("carga-archivos", _("File upload and validation")),
            opcion("conciliacion", _("Bank reconciliation")),
            opcion("depositos", _("Bank deposits")),
            opcion("ordenes-pago", _("Payment orders")),
            opcion("entrega-cheques", _("Check delivery")),
            opcion("planilla-fiscal", _("Generate tax form")),
        ],
        # Reportes (Reports): listados para imprimir o exportar.
        "reportes": [
            opcion("movimientos-banco", _("Bank movements")),
            opcion("conciliacion", _("Bank reconciliation")),
            opcion("movimientos-caja", _("Cash movements")),
            opcion("depositos", _("Bank deposits")),
            opcion("ordenes-pago", _("Payment orders")),
            opcion("cuentas-bancarias", _("Bank accounts")),
            opcion("chequeras", _("Checkbooks")),
            opcion("cajas", _("Cash registers")),
            opcion("tablas", _("Cash & Banks tables")),
            opcion("estado-cuenta-bancos", _("Account statement (bank accounts)")),
            opcion("estado-cuenta-cajas", _("Account statement (cash registers)")),
            opcion("estado-financiero", _("Financial statement")),
            opcion("flujo-caja", _("Cash flow")),
        ],
        # Consultas (Queries): consultas rápidas en pantalla.
        "consultas": [
            opcion("saldos-cuentas", _("Account balances")),
            opcion("movimientos", _("Movements")),
            opcion("historial-tasas", _("Exchange rate history")),
        ],
    },
}
