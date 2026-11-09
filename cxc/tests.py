"""
cxc/tests.py
============

Pruebas automáticas del módulo Ventas y Cuentas por Cobrar (no necesitan SQL Server):
    python manage.py test cxc --settings=sistema.settings_prueba

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
    modulo = "cxc"          # carpeta del módulo que se prueba


class TablasTests(pruebas.ConEmpresa):
    def tablas(self, modulo):
        return next(s for s in modulos.buscar_modulo(modulo)["secciones"] if s["clave"] == "tablas")

    def test_tablas_en_el_orden_pedido(self):
        """Ventas y Cuentas por Cobrar › Tablas tiene las 16 opciones, en este orden."""
        self.assertEqual([o["clave"] for o in self.tablas("cxc")["opciones"]], [
            "clientes", "tipos-cliente", "zonas", "segmentos", "vendedores", "paises", "almacenes",
            "sucursales", "condiciones-pago", "transportes", "puntos-tarjetas", "cuentas-ingreso-egreso",
            "descuentos", "comisiones", "moneda", "turnos-pos"])

    def test_almacenes_y_sucursales_son_las_de_inventario(self):
        """Almacenes y Sucursales llevan a la misma pantalla que en Inventario."""
        cxc = {o["clave"]: o for o in self.tablas("cxc")["opciones"]}
        inv = {o["clave"]: o for o in self.tablas("inventario")["opciones"]}
        for clave in ("almacenes", "sucursales"):
            self.assertEqual(cxc[clave]["url"], inv[clave]["url"])
            self.assertTrue(cxc[clave]["url"].startswith("/inventario/"))

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("cxc:inicio"))
        for texto in ("Clientes", "Tipos de Clientes", "Zonas", "Segmentos", "Vendedores", "Países",
                      "Almacenes", "Sucursales", "Condiciones de Pago", "Transportes",
                      "Puntos - Tarjetas de Crédito/Débito", "Cuentas de Ingreso/Egreso", "Descuentos",
                      "Comisiones", "Moneda", "Turnos Punto de Venta", "Compartida con Inventario"):
            self.assertContains(r, texto)


class ProcesosTests(pruebas.ConEmpresa):
    def test_procesos_en_el_orden_pedido(self):
        """Ventas y Cuentas por Cobrar › Procesos tiene las 12 opciones, en este orden."""
        procesos = next(s for s in modulos.buscar_modulo("cxc")["secciones"] if s["clave"] == "procesos")
        self.assertEqual([o["clave"] for o in procesos["opciones"]], [
            "facturas", "pedidos", "cotizaciones", "devoluciones", "notas-entrega", "plantillas-venta",
            "turnos", "documentos-venta", "cobranza", "giros", "empaques", "control-empaques"])

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("cxc:inicio"))
        for texto in ("Facturas de Venta", "Pedidos", "Cotizaciones a Clientes", "Devoluciones de Clientes",
                      "Notas de Entrega", "Plantillas de Venta",
                      "Pedidos", "Cotizaciones a Clientes", "Iniciar y Cerrar Turnos",
                      "Documentos de Ventas", "Cobranza", "Generar Giros", "Empaques", "Control de Empaques"):
            self.assertContains(r, texto)


class ReportesTests(pruebas.ConEmpresa):
    def test_reportes_en_el_orden_pedido(self):
        """Ventas y Cuentas por Cobrar › Reportes tiene los 20 reportes, en este orden."""
        reportes = next(s for s in modulos.buscar_modulo("cxc")["secciones"] if s["clave"] == "reportes")
        self.assertEqual([o["clave"] for o in reportes["opciones"]], [
            "clientes", "vendedores", "facturas", "pedidos", "cotizaciones", "devoluciones",
            "notas-entrega", "notas-despacho", "plantillas-venta", "documentos-cxc", "punto-venta",
            "empaques", "cobranza", "tablas", "libro-ventas", "estado-cuenta", "vencimientos",
            "analisis-ventas", "estadisticas-ventas", "margen-ganancia"])

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("cxc:inicio"))
        for texto in ("Notas de Despacho", "Plantillas de Venta", "Documentos de CxC", "Punto de Ventas",
                      "Tablas de Ventas y CxC", "Libro de Ventas", "Estado de Cuenta de Clientes",
                      "Análisis del Vencimiento/Por Vencer de Clientes", "Análisis de Ventas",
                      "Estadísticas de Ventas", "Margen de Ganancia en Ventas"):
            self.assertContains(r, texto)


class NombresPedidosCotizacionesTests(pruebas.ConEmpresa):
    """En inglés: Packing List y Proforma. En español: Pedidos y Cotizaciones a Clientes."""

    def test_en_ingles(self):
        r = self.client.get(reverse("cxc:inicio"))
        self.assertContains(r, "Packing List")
        self.assertContains(r, "Proforma")

    @override_settings(LANGUAGE_CODE="es")
    def test_en_espanol(self):
        r = self.client.get(reverse("cxc:inicio"))
        # Títulos que se VEN en el menú (el buscador, aparte, guarda los dos idiomas a propósito).
        cxc = next(m for m in r.context["menu_modulos"] if m["nombre"] == "cxc")
        titulos = [str(o["titulo"]) for s in cxc["secciones"] for o in modulos.hojas(s)]
        self.assertNotIn("Packing List", titulos)
        self.assertNotIn("Proforma", titulos)
        self.assertEqual(titulos.count("Pedidos"), 2)                    # en Procesos y en Reportes
        self.assertEqual(titulos.count("Cotizaciones a Clientes"), 2)
        # Y el buscador sí las encuentra por su nombre en inglés:
        pedidos = next(o for o in r.context["indice_menu"] if o["u"].endswith("/procesos/pedidos/"))
        self.assertIn("Packing List", pedidos["k"])
