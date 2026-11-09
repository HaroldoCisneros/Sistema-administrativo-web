"""
inventario/tests.py
===================

Pruebas automáticas del módulo Inventario (no necesitan SQL Server):
    python manage.py test inventario --settings=sistema.settings_prueba

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
    modulo = "inventario"          # carpeta del módulo que se prueba


class TablasTests(pruebas.ConEmpresa):
    def test_tablas_en_el_orden_pedido(self):
        """Inventario › Tablas tiene las 12 opciones, en este orden."""
        tablas = next(s for s in modulos.buscar_modulo("inventario")["secciones"] if s["clave"] == "tablas")
        self.assertEqual([o["clave"] for o in tablas["opciones"]], [
            "articulos", "articulos-compuestos", "lineas", "categorias", "sublineas", "procedencias",
            "colores", "unidades", "sucursales", "almacenes", "tipos-ajuste", "proveedores"])

    def test_proveedores_es_la_misma_pantalla_que_en_cxp(self):
        """Proveedores en Inventario lleva a la misma pantalla que en Compras y Cuentas por Pagar."""
        def proveedores(modulo):
            m = modulos.buscar_modulo(modulo)
            tablas = next(s for s in m["secciones"] if s["clave"] == "tablas")
            return next(o for o in tablas["opciones"] if o["clave"] == "proveedores")
        self.assertEqual(proveedores("inventario")["url"], proveedores("cxp")["url"])
        self.assertEqual(proveedores("inventario")["url"], "/cxp/tablas/proveedores/")

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("inventario:inicio"))
        for texto in ("Artículos Compuestos", "Líneas de Artículo", "Categorías de Artículo", "Sub-líneas",
                      "Procedencias", "Colores", "Unidades", "Sucursales", "Almacenes", "Tipos de Ajuste", "Proveedores",
                      "Compartida con Compras y Cuentas por Pagar"):
            self.assertContains(r, texto)


class ProcesosTests(pruebas.ConEmpresa):
    def procesos(self):
        return next(s for s in modulos.buscar_modulo("inventario")["secciones"] if s["clave"] == "procesos")

    def test_procesos_en_el_orden_pedido(self):
        """Procesos: 3 opciones sueltas y 2 grupos, en el orden pedido."""
        self.assertEqual([o["clave"] for o in self.procesos()["opciones"]], [
            "ajustes", "traslados", "conteo-fisico", "ajuste-precios", "generacion-compuestos"])
        self.assertEqual(self.procesos()["total"], 7)        # 3 sueltas + 2 + 2 sub-opciones

    def test_sub_opciones_abren_en_construccion(self):
        r = self.client.get("/inventario/procesos/conteo-fisico/preparar-cerrar/")
        self.assertContains(r, "Prepare and close count")
        self.assertContains(r, "Physical inventory count")       # el grupo en las migas de pan
        r = self.client.get("/inventario/procesos/ajuste-precios/automatico/")
        self.assertEqual(r.status_code, 200)
        # Un grupo no es una opción: su dirección suelta no existe.
        self.assertEqual(self.client.get("/inventario/procesos/conteo-fisico/").status_code, 404)
        self.assertEqual(self.client.get("/inventario/procesos/conteo-fisico/no-existe/").status_code, 404)

    def test_grupo_abierto_en_el_menu(self):
        """Estando en una sub-opción, el menú deja abierto su grupo."""
        r = self.client.get("/inventario/procesos/ajuste-precios/manual/")
        inv = next(m for m in r.context["menu_modulos"] if m["nombre"] == "inventario")
        procesos = next(s for s in inv["secciones"] if s["clave"] == "procesos")
        grupo = next(o for o in procesos["opciones"] if o["clave"] == "ajuste-precios")
        self.assertTrue(grupo["activa"])
        self.assertTrue(procesos["activa"])

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("inventario:inicio"))
        for texto in ("Ajustes de Inventario", "Traslados de Inventario entre Almacenes",
                      "Conteo de Inventario Físico", "Preparar y Cerrar Físico", "Ingresar Resultados Físico",
                      "Ajuste de Precios", "Automático", "Manual", "Generación de Compuestos"):
            self.assertContains(r, texto)


class ReportesTests(pruebas.ConEmpresa):
    def test_reportes_en_el_orden_pedido(self):
        """Inventario › Reportes tiene los 7 reportes, en este orden."""
        reportes = next(s for s in modulos.buscar_modulo("inventario")["secciones"] if s["clave"] == "reportes")
        self.assertEqual([o["clave"] for o in reportes["opciones"]], [
            "articulos", "ajustes", "traslados", "inventario-fisico", "movimientos", "tablas",
            "compuestos-generados"])

    @override_settings(LANGUAGE_CODE="es")
    def test_nombres_en_espanol(self):
        r = self.client.get(reverse("inventario:inicio"))
        for texto in ("Ajustes de Entrada y Salida", "Traslados entre Almacenes", "Inventario Físico",
                      "Movimientos de Inventario", "Tablas de Inventario", "Compuestos Generados"):
            self.assertContains(r, texto)
