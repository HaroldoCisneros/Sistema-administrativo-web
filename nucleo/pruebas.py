"""
nucleo/pruebas.py
=================

Herramientas para las pruebas automáticas, compartidas por todos los módulos.

    ConEmpresa      prueba con un usuario que ya inició sesión y eligió empresa
    PruebasModulo   pruebas que TODO módulo de trabajo debe pasar
                    (cada módulo la usa en su tests.py indicando su nombre)

Ejemplo (cxc/tests.py):
    from nucleo import pruebas

    class MenuTests(pruebas.PruebasModulo):
        modulo = "cxc"
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape        # "Cash & Banks" -> "Cash &amp; Banks" (como sale en el HTML)

from empresas import sesion
from empresas.models import Empresa

from . import modulos


class ConEmpresa(TestCase):
    """Deja listo un usuario con sesión iniciada y la empresa PRUEBA elegida."""

    def setUp(self):
        # Empresa de prueba (en la base temporal en memoria).
        self.empresa = Empresa.objects.create(codigo="PRUEBA", nombre="Test Company",
                                              base_profit="BD_PRUEBA", rif="J-00000000-0")
        # Usuario de prueba con su sesión iniciada.
        self.usuario = get_user_model().objects.create_user("HCIS", first_name="HAROLDO CISNEROS")
        self.client.force_login(self.usuario)
        # Guarda la empresa en la sesión, igual que la pantalla de elegir empresa.
        s = self.client.session                        # la sesión del navegador de prueba
        s[sesion.CLAVE] = self.empresa.codigo
        s.save()


class PruebasModulo(ConEmpresa):
    """
    Pruebas comunes de un módulo. La clase hija indica "modulo".
    Si "modulo" está vacío (esta misma clase), las pruebas se saltan.
    """
    modulo = ""

    def setUp(self):
        if not self.modulo:
            self.skipTest("Clase base: la usa cada módulo")
        super().setUp()
        self.datos = modulos.buscar_modulo(self.modulo)

    def test_esta_en_el_menu_con_sus_4_secciones(self):
        """El módulo aparece en el menú con Tables, Processes, Reports y Queries, en ese orden."""
        self.assertIsNotNone(self.datos, "El módulo no está en settings.MODULOS_MENU")
        claves = [s["clave"] for s in self.datos["secciones"]]
        self.assertEqual(claves, ["tablas", "procesos", "reportes", "consultas"])

    def test_claves_de_opciones_sin_repetir(self):
        """Dentro de cada sección no puede haber dos opciones con la misma clave."""
        for s in self.datos["secciones"]:
            claves = [o["clave"] for o in s["opciones"]]
            self.assertEqual(len(claves), len(set(claves)), f"Clave repetida en {s['clave']}")
            for g in (o for o in s["opciones"] if o.get("grupo")):     # y dentro de cada grupo
                claves = [h["clave"] for h in g["hijas"]]
                self.assertEqual(len(claves), len(set(claves)), f"Clave repetida en {g['clave']}")

    def test_pagina_del_modulo(self):
        """La página del módulo abre y muestra su título y sus 4 secciones."""
        r = self.client.get(reverse(f"{self.modulo}:inicio"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, escape(self.datos["titulo"]))
        for titulo in ("Tables", "Processes", "Reports", "Queries"):
            self.assertContains(r, titulo)

    def test_cada_opcion_abre(self):
        """Todas las opciones del menú abren (su pantalla o "Under construction")."""
        for s in self.datos["secciones"]:
            for o in modulos.hojas(s):                     # sueltas y dentro de grupos
                r = self.client.get(o["url"])
                self.assertEqual(r.status_code, 200, o["url"])
                if o["pendiente"]:
                    self.assertContains(r, "under construction")

    def test_opcion_inexistente_da_404(self):
        """Una dirección escrita a mano con una opción que no existe responde 404."""
        r = self.client.get(reverse(f"{self.modulo}:pendiente",
                                    kwargs={"seccion": "tablas", "opcion": "no-existe"}))
        self.assertEqual(r.status_code, 404)
