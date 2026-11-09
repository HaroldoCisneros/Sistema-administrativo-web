"""
cajas_bancos/tests.py
=====================

Pruebas automáticas del módulo Cajas y Bancos (no necesitan SQL Server):
    python manage.py test cajas_bancos --settings=sistema.settings_prueba

Las pruebas comunes a todos los módulos (el menú tiene las 4 secciones, la
página del módulo abre, las opciones llevan a "Under construction", ...)
están en nucleo/pruebas.py; aquí solo se indica qué módulo probar.
Las pruebas propias de cada pantalla se agregan debajo.
"""

# Se importa el archivo (no la clase) para que Django no corra la clase base sola.
from django.test import override_settings
from django.urls import reverse

from nucleo import modulos, pruebas


class MenuTests(pruebas.PruebasModulo):
    modulo = "cajas_bancos"          # carpeta del módulo que se prueba


class TablasTests(pruebas.ConEmpresa):
    def tablas(self, modulo):
        return next(s for s in modulos.buscar_modulo(modulo)["secciones"] if s["clave"] == "tablas")

    def test_tablas_en_el_orden_pedido(self):
        """Cajas y Bancos › Tablas tiene las 7 opciones, en este orden."""
        self.assertEqual([o["clave"] for o in self.tablas("cajas_bancos")["opciones"]], [
            "cuentas-bancarias", "chequeras", "cajas", "bancos", "beneficiarios",
            "cuentas-ingreso-egreso", "tarjetas"])

    def test_tablas_comunes_con_ventas(self):
        cyb = {o["clave"]: o for o in self.tablas("cajas_bancos")["opciones"]}
        cxc = {o["clave"]: o for o in self.tablas("cxc")["opciones"]}
        self.assertEqual(cyb["cuentas-ingreso-egreso"]["url"], cxc["cuentas-ingreso-egreso"]["url"])
        self.assertEqual(cyb["tarjetas"]["url"], cxc["puntos-tarjetas"]["url"])

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("cajas_bancos:inicio"))
        for texto in ("Cuentas Bancarias", "Chequeras", "Cajas", "Bancos", "Beneficiarios",
                      "Cuentas de Ingreso/Egreso", "Tarjetas de Crédito/Débito",
                      "Compartida con Ventas y Cuentas por Cobrar"):
            self.assertContains(r, texto)


class ProcesosTests(pruebas.ConEmpresa):
    def test_procesos_en_el_orden_pedido(self):
        """Cajas y Bancos › Procesos tiene las 8 opciones, en este orden."""
        procesos = next(s for s in modulos.buscar_modulo("cajas_bancos")["secciones"] if s["clave"] == "procesos")
        self.assertEqual([o["clave"] for o in procesos["opciones"]], [
            "movimientos-caja", "movimientos-banco", "carga-archivos", "conciliacion", "depositos",
            "ordenes-pago", "entrega-cheques", "planilla-fiscal"])

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("cajas_bancos:inicio"))
        for texto in ("Movimientos de Cajas", "Movimientos de Bancos", "Carga y Validación de Archivos",
                      "Conciliación Bancaria", "Depósitos Bancarios", "Órdenes de Pago",
                      "Entrega de Cheques", "Generar Planilla Fiscal"):
            self.assertContains(r, texto)


class ReportesTests(pruebas.ConEmpresa):
    def test_reportes_en_el_orden_pedido(self):
        """Cajas y Bancos › Reportes tiene los 13 reportes, en este orden."""
        reportes = next(s for s in modulos.buscar_modulo("cajas_bancos")["secciones"] if s["clave"] == "reportes")
        self.assertEqual([o["clave"] for o in reportes["opciones"]], [
            "movimientos-banco", "conciliacion", "movimientos-caja", "depositos", "ordenes-pago",
            "cuentas-bancarias", "chequeras", "cajas", "tablas", "estado-cuenta-bancos",
            "estado-cuenta-cajas", "estado-financiero", "flujo-caja"])

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get("/cajas-bancos/reportes/tablas/")
        self.assertContains(r, "Tablas de Cajas y Bancos")
        r = self.client.get(reverse("cajas_bancos:inicio"))
        for texto in ("Estado de Cuenta (Ctas Bancarias)", "Estado de Cuenta (Cajas)",
                      "Estado Financiero", "Flujo de Caja"):
            self.assertContains(r, texto)
