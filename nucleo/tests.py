"""
nucleo/tests.py
===============

Pruebas automáticas del núcleo (no necesitan SQL Server):
    python manage.py test nucleo --settings=sistema.settings_prueba
"""

import datetime as dt
from decimal import Decimal

from django.db import connections
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import translation
from django.urls import reverse

from empresas.models import Empresa

from . import modulos, profit
from .pruebas import ConEmpresa
from .management.commands.compilar_idiomas import leer_po
from .templatetags.formato import iniciales


class InicioTests(ConEmpresa):
    def test_muestra_los_5_modulos_y_la_empresa(self):
        """El tablero muestra los 5 módulos, la marca y la empresa elegida."""
        r = self.client.get(reverse("nucleo:inicio"))
        self.assertEqual(r.status_code, 200)
        for titulo in ("Inventory", "Sales &amp; Accounts Receivable", "Purchasing &amp; Accounts Payable",
                       "Cash &amp; Banks", "Maintenance"):
            self.assertContains(r, titulo)
        self.assertContains(r, 'class="marca')                # marca provisional (sin logo)
        self.assertContains(r, "PRUEBA")                    # código de la empresa en la barra
        self.assertContains(r, "BD_PRUEBA")                 # base de Profit en "Your session"

    def test_buscador_recibe_todas_las_opciones(self):
        """La lista para el buscador va en la página como JSON."""
        r = self.client.get(reverse("nucleo:inicio"))
        self.assertContains(r, 'id="indice-menu"')
        total = sum(m["total"] for m in modulos.estructura())
        self.assertEqual(len(r.context["indice_menu"]), total)

    def test_marca_la_opcion_actual(self):
        """En "Under construction", el menú marca el módulo, la sección y la opción actuales."""
        url = reverse("cxc:pendiente", kwargs={"seccion": "procesos", "opcion": "cobranza"})
        r = self.client.get(url)
        cxc = next(m for m in r.context["menu_modulos"] if m["nombre"] == "cxc")
        self.assertTrue(cxc["activo"])
        procesos = next(s for s in cxc["secciones"] if s["clave"] == "procesos")
        self.assertTrue(procesos["activa"])
        self.assertContains(r, 'aria-current="page">Collections')


class SinSesionTests(TestCase):
    def test_inicio_requiere_sesion(self):
        """Sin sesión, la pantalla de inicio manda al login."""
        r = self.client.get(reverse("nucleo:inicio"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("cuentas:entrar"), r["Location"])


class EstructuraTests(SimpleTestCase):
    def test_cinco_modulos_en_orden(self):
        nombres = [m["nombre"] for m in modulos.estructura()]
        self.assertEqual(nombres, ["inventario", "cxc", "cxp", "cajas_bancos", "mantenimiento"])

    def test_opcion_con_url_mal_escrita_queda_pendiente(self):
        """Una ruta que no existe no rompe el menú: la opción lleva a "Under construction"."""
        url = modulos._url_opcion("cxc", "tablas", modulos.opcion("x", "X", url="cxc:no_existe"))
        self.assertEqual(url, "/cxc/tablas/x/")


class ProfitTests(TestCase):
    def test_conexion_por_empresa(self):
        """Cada empresa tiene su conexión, que apunta a SU base de Profit."""
        e = Empresa(codigo="CF01", nombre="X", base_profit="BASE_CF01")
        alias = profit.conexion_empresa(e)
        # Al terminar la prueba se quita la conexión creada (Django revisa las
        # conexiones al cerrar cada grupo de pruebas y no espera una nueva).
        self.addCleanup(connections.databases.pop, alias)
        self.assertEqual(alias, "profit_CF01")
        self.assertEqual(connections.databases[alias]["NAME"], "BASE_CF01")

    def test_num(self):
        self.assertEqual(profit.num(None), 0.0)                      # NULL -> 0
        self.assertEqual(profit.num(Decimal("1.234567"), 2), 1.23)

    def test_fecha_vacia_de_profit(self):
        self.assertIsNone(profit.fecha(dt.datetime(1900, 1, 1)))     # fecha "vacía"
        self.assertEqual(profit.fecha(dt.datetime(2026, 3, 25, 10, 5)), "2026-03-25")

    def test_val_de_foxpro(self):
        self.assertEqual(profit.val(" 12 "), 12.0)
        self.assertEqual(profit.val("abc"), 0.0)                     # texto inválido -> 0


class EtiquetasTests(SimpleTestCase):
    def test_iniciales(self):
        self.assertEqual(iniciales("HAROLDO CISNEROS"), "HC")
        self.assertEqual(iniciales("HCIS"), "HC")
        self.assertEqual(iniciales(""), "?")

    def test_icono(self):
        html = Template('{% load iconos %}{% icono "inicio" %}').render(Context())
        self.assertIn("iconos.svg#i-inicio", html)


# =============================================================================
# Idiomas
# =============================================================================
@override_settings(LANGUAGE_CODE="es")
class EspanolTests(ConEmpresa):
    """Con <idioma>es</idioma> en config.xml, todo sale en español."""

    def test_tablero_en_espanol(self):
        r = self.client.get(reverse("nucleo:inicio"))
        self.assertContains(r, '<html lang="es">')
        for texto in ("Ventas y Cuentas por Cobrar", "Compras y Cuentas por Pagar", "Cajas y Bancos",
                      "Mantenimiento", "Tu sesión", "Cambiar de empresa", "Sistema Administrativo"):
            self.assertContains(r, texto)
        self.assertNotContains(r, "Sales &amp; Accounts Receivable</strong>")

    def test_pagina_de_modulo_y_pendiente(self):
        r = self.client.get(reverse("cxc:inicio"))
        for texto in ("Tablas", "Procesos", "Reportes", "Consultas", "Clientes", "Pronto"):
            self.assertContains(r, texto)
        r = self.client.get(reverse("cxc:pendiente", kwargs={"seccion": "procesos", "opcion": "cobranza"}))
        self.assertContains(r, "Esta opción está en construcción")
        self.assertContains(r, "Volver a Ventas y Cuentas por Cobrar")

    def test_buscador_encuentra_en_los_dos_idiomas(self):
        """Las palabras de búsqueda llevan el nombre en inglés y en español."""
        r = self.client.get(reverse("nucleo:inicio"))
        cobranza = next(o for o in r.context["indice_menu"] if o["u"].endswith("/procesos/cobranza/"))
        self.assertEqual(cobranza["t"], "Cobranza")
        self.assertIn("Collections", cobranza["k"])
        self.assertIn("Cobranza", cobranza["k"])

    def test_login_en_espanol(self):
        self.client.logout()
        r = self.client.get(reverse("cuentas:entrar"))
        self.assertContains(r, "Iniciar sesión")
        self.assertContains(r, "Contraseña")
        self.assertContains(r, ">Usuario</label>")              # la nuestra, no la de Django


# Palabras que se escriben igual en inglés y en español (la prueba no las
# toma como "sin traducir").
IGUALES_EN_AMBOS = {"Manual"}


class TraduccionesTests(SimpleTestCase):
    def test_todo_texto_del_menu_tiene_traduccion(self):
        """Cada opción, sección y módulo tiene su traducción al español."""
        for m in modulos.estructura():
            textos = [m["titulo"], m["descripcion"]] + [s["titulo"] for s in m["secciones"]] + \
                     [o["titulo"] for s in m["secciones"] for o in s["opciones"]] + \
                     [h["titulo"] for s in m["secciones"] for h in modulos.hojas(s)]
            for texto in textos:
                with translation.override("en"):
                    ingles = str(texto)
                with translation.override("es"):
                    espanol = str(texto)
                if ingles in IGUALES_EN_AMBOS:
                    continue
                self.assertNotEqual(ingles, espanol, f"Falta traducir: {ingles}")

    def test_mo_al_dia_con_po(self):
        """Los .mo compilados tienen las mismas traducciones que los .po (se corrió compilar_idiomas)."""
        import gettext
        from pathlib import Path
        from django.conf import settings
        for po in Path(settings.BASE_DIR).glob("*/locale/*/LC_MESSAGES/django.po"):
            mo = gettext.GNUTranslations(po.with_suffix(".mo").open("rb"))
            for original, traducido in leer_po(po).items():
                if original:
                    self.assertEqual(mo.gettext(original), traducido, f"{po}: {original}")
