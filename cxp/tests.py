"""
cxp/tests.py
============

Pruebas automáticas del módulo Compras y Cuentas por Pagar (no necesitan SQL Server):
    python manage.py test cxp --settings=sistema.settings_prueba

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
    modulo = "cxp"          # carpeta del módulo que se prueba


class TablasTests(pruebas.ConEmpresa):
    def tablas(self, modulo):
        return next(s for s in modulos.buscar_modulo(modulo)["secciones"] if s["clave"] == "tablas")

    def test_tablas_en_el_orden_pedido(self):
        """Compras y Cuentas por Pagar › Tablas tiene las 7 opciones, en este orden."""
        self.assertEqual([o["clave"] for o in self.tablas("cxp")["opciones"]], [
            "proveedores", "tipos-proveedor", "zonas", "segmentos", "condiciones-pago",
            "cuentas-ingreso-egreso", "convenios"])

    def test_tablas_comunes_con_ventas(self):
        """Zonas, Segmentos, Condiciones de Pago y Cuentas de Ingreso/Egreso son las de Ventas."""
        cxp = {o["clave"]: o for o in self.tablas("cxp")["opciones"]}
        cxc = {o["clave"]: o for o in self.tablas("cxc")["opciones"]}
        for clave in ("zonas", "segmentos", "condiciones-pago", "cuentas-ingreso-egreso"):
            self.assertEqual(cxp[clave]["url"], cxc[clave]["url"])

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("cxp:inicio"))
        for texto in ("Compras y Cuentas por Pagar", "Proveedores", "Tipos de Proveedores", "Zonas",
                      "Segmentos", "Condiciones de Pago", "Cuentas de Ingreso/Egreso", "Convenios",
                      "Compartida con Ventas y Cuentas por Cobrar"):
            self.assertContains(r, texto)


class ProcesosTests(pruebas.ConEmpresa):
    def procesos(self):
        return next(s for s in modulos.buscar_modulo("cxp")["secciones"] if s["clave"] == "procesos")

    def test_procesos_en_el_orden_pedido(self):
        """Compras y Cuentas por Pagar › Procesos: 12 opciones (una es un grupo con 2 sub-opciones)."""
        self.assertEqual([o["clave"] for o in self.procesos()["opciones"]], [
            "facturas-compra", "ordenes-compra", "cotizaciones", "devoluciones", "notas-recepcion",
            "plantillas-compra", "importaciones", "control-importaciones", "documentos",
            "programacion-pagos", "pagos", "giros"])
        self.assertEqual(self.procesos()["total"], 13)       # 11 sueltas + 2 sub-opciones

    def test_sub_opciones_de_importaciones(self):
        r = self.client.get("/cxp/procesos/control-importaciones/distribucion-costos/")
        self.assertContains(r, "Cost distribution")
        self.assertEqual(self.client.get("/cxp/procesos/control-importaciones/expediente/").status_code, 200)

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("cxp:inicio"))
        for texto in ("Facturas de Compra", "Órdenes de Compra", "Cotizaciones de Proveedores",
                      "Devoluciones a Proveedores", "Notas de Recepción", "Plantillas de Compra",
                      "Importaciones", "Control de Importaciones", "Distribución de Costos", "Expediente",
                      "Documentos", "Programación de Pagos", "Pagos a Proveedores", "Generar Giros"):
            self.assertContains(r, texto)


class ReportesTests(pruebas.ConEmpresa):
    def test_reportes_en_el_orden_pedido(self):
        """Compras y Cuentas por Pagar › Reportes tiene los 19 reportes, en este orden."""
        reportes = next(s for s in modulos.buscar_modulo("cxp")["secciones"] if s["clave"] == "reportes")
        self.assertEqual([o["clave"] for o in reportes["opciones"]], [
            "proveedores", "facturas-compra", "ordenes-compra", "cotizaciones", "devoluciones",
            "notas-recepcion", "plantillas-compra", "importaciones", "distribucion-costos",
            "documentos-cxp", "pagos-autorizados", "pagos", "cheques-emitidos", "tablas",
            "libro-compras", "estado-cuenta", "vencimientos", "analisis-compras", "estadisticas-compras"])

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("cxp:inicio"))
        for texto in ("Documentos de CxP", "Pagos Autorizados", "Formato de Cheques Emitidos",
                      "Tablas de Compras y CxP", "Libro de Compras", "Estado de Cuenta de Proveedores",
                      "Análisis del Vencimiento/Por Vencer de Proveedor", "Análisis de Compras",
                      "Estadísticas de Compras"):
            self.assertContains(r, texto)
        r = self.client.get("/cxp/reportes/pagos/")
        self.assertContains(r, "<h1>Pagos</h1>")
