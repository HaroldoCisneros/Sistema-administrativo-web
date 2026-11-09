"""
empresas/tests.py
=================

Pruebas automáticas de la elección de empresa (no necesitan SQL Server):
    python manage.py test empresas --settings=sistema.settings_prueba
"""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase
from django.urls import reverse

from . import sesion
from .models import Empresa


class SeleccionarTests(TestCase):
    def setUp(self):
        self.cf = Empresa.objects.create(codigo="CF01", nombre="Empresa Uno", base_profit="BD_CF")
        Empresa.objects.create(codigo="OLD", nombre="Old company", base_profit="BD_OLD", activa=False)
        self.client.force_login(get_user_model().objects.create_user("HCIS"))

    def elegir(self, codigo, siguiente=""):
        return self.client.post(reverse("empresas:seleccionar"), {"codigo": codigo, "next": siguiente})

    def test_sin_empresa_lo_manda_a_elegirla(self):
        """Con sesión pero sin empresa, cualquier pantalla de trabajo lleva a elegir empresa."""
        destino = reverse("cxc:inicio")
        r = self.client.get(destino)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r["Location"].startswith(reverse("empresas:seleccionar")))
        self.assertIn("next=", r["Location"])

    def test_muestra_solo_las_activas(self):
        r = self.client.get(reverse("empresas:seleccionar"))
        self.assertContains(r, "Empresa Uno")
        self.assertNotContains(r, "Old company")

    def test_codigo_correcto_en_minusculas(self):
        """El código se acepta en minúsculas, queda en la sesión y va al inicio."""
        r = self.elegir("cf01")
        self.assertRedirects(r, reverse("nucleo:inicio"))
        self.assertEqual(self.client.session[sesion.CLAVE], "CF01")
        self.assertEqual(r.cookies["ultima_empresa"].value, "CF01")   # se recuerda la última

    def test_regresa_a_donde_iba(self):
        destino = reverse("cxp:inicio")
        r = self.elegir("CF01", destino)
        self.assertRedirects(r, destino)

    def test_next_de_otro_sitio_se_ignora(self):
        """Un ?next= que apunta a otra página web se ignora (seguridad)."""
        r = self.elegir("CF01", "https://sitio-malo.com/")
        self.assertRedirects(r, reverse("nucleo:inicio"))

    def test_codigo_inexistente_o_inactivo(self):
        for codigo in ("NOEXISTE", "OLD", ""):
            r = self.elegir(codigo)
            self.assertEqual(r.status_code, 200)
            self.assertNotIn(sesion.CLAVE, self.client.session)
        self.assertContains(self.elegir("OLD"), "isn&#x27;t available to you")

    def test_empresa_desactivada_despues_pide_otra(self):
        """Si la empresa se desactiva mientras se trabaja, el sistema pide elegir otra."""
        self.elegir("CF01")
        Empresa.objects.filter(codigo="CF01").update(activa=False)
        r = self.client.get(reverse("nucleo:inicio"))
        self.assertTrue(r["Location"].startswith(reverse("empresas:seleccionar")))


class LoginOlvidaEmpresaTests(TestCase):
    def test_al_iniciar_sesion_se_vuelve_a_pedir(self):
        """Cada vez que alguien inicia sesión, la empresa se pide de nuevo."""
        Empresa.objects.create(codigo="CF01", nombre="X", base_profit="BD")
        get_user_model().objects.create_user("ADMIN", password="clave-larga-123")
        # Sesión (todavía sin usuario) que ya trae una empresa guardada:
        s = self.client.session
        s[sesion.CLAVE] = "CF01"
        s.save()
        self.client.post(reverse("cuentas:entrar"), {"username": "ADMIN", "password": "clave-larga-123"})
        self.assertNotIn(sesion.CLAVE, self.client.session)


class ComandoTests(TestCase):
    def test_crear_y_actualizar(self):
        salida = StringIO()
        call_command("crear_empresa", "cf01", "Empresa", "BD_CF", "--rif", "J-1", stdout=salida)
        self.assertIn("created", salida.getvalue())
        call_command("crear_empresa", "CF01", "Empresa Uno", "BD_CF", stdout=salida)
        e = Empresa.objects.get(codigo="CF01")
        self.assertEqual(e.nombre, "Empresa Uno")
        self.assertEqual(Empresa.objects.count(), 1)

    def test_base_con_caracteres_raros(self):
        with self.assertRaises(CommandError):
            call_command("crear_empresa", "CF02", "X", "BD; DROP TABLE", stdout=StringIO())
