"""
cuentas/tests.py
================

Pruebas automáticas del inicio de sesión (no necesitan SQL Server: la lectura
de la tabla de usuarios de Profit se simula con mock).

    python manage.py test cuentas --settings=sistema.settings_prueba
"""

from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .encriptacion import clave_coincide, encriptar


def guardada(clave):
    """Así queda la clave en employee.password: encriptada y rellenada a 15 con espacios."""
    return encriptar(clave).ljust(15, b" ")


class EncriptacionTests(TestCase):
    def test_formula_de_foxpro(self):
        # CHR(((ASC("A")+17)*11)%255) = CHR(137)
        self.assertEqual(encriptar("A"), bytes([137]))
        self.assertEqual(encriptar("1"), bytes([((49 + 17) * 11) % 255]))

    def test_coincide_con_relleno(self):
        self.assertTrue(clave_coincide("abc123", guardada("abc123")))
        self.assertFalse(clave_coincide("abc124", guardada("abc123")))
        self.assertFalse(clave_coincide("", guardada("abc123")))

    def test_clave_que_termina_en_llave(self):
        # '}' se encripta como espacio: no debe romper la comparación
        self.assertEqual(encriptar("}"), b" ")
        self.assertTrue(clave_coincide("ab}", guardada("ab}")))

    def test_mayusculas(self):
        self.assertFalse(clave_coincide("clave", guardada("CLAVE")))
        self.assertTrue(clave_coincide("clave", guardada("CLAVE"), mayusculas=True))

    def test_caracter_fuera_de_windows_1252(self):
        self.assertFalse(clave_coincide("clave😀", guardada("clave")))


EMPLEADO = {"codigo": "HCIS", "nombre": "HAROLDO CISNEROS", "clave": guardada("secreta"),
            "activo": True, "estado": "A"}


@override_settings(INTENTOS_LOGIN=3)
class LoginTests(TestCase):
    def setUp(self):
        cache.clear()
        parche = mock.patch("cuentas.backends.leer_empleado",
                            side_effect=lambda c: dict(EMPLEADO) if c == "HCIS" else None)
        self.leer = parche.start()
        self.addCleanup(parche.stop)

    def entrar(self, usuario, clave):
        return self.client.post(reverse("cuentas:entrar"), {"username": usuario, "password": clave})

    def test_login_correcto_crea_usuario_espejo(self):
        r = self.entrar("hcis", "secreta")
        self.assertRedirects(r, reverse("nucleo:inicio"), fetch_redirect_response=False)
        u = get_user_model().objects.get(username="HCIS")
        self.assertEqual(u.first_name, "HAROLDO CISNEROS")
        self.assertFalse(u.has_usable_password())

    def test_clave_incorrecta(self):
        r = self.entrar("HCIS", "otra")
        self.assertContains(r, "Incorrect username or password")

    def test_usuario_inactivo(self):
        self.leer.side_effect = lambda c: dict(EMPLEADO, activo=False)
        r = self.entrar("HCIS", "secreta")
        self.assertContains(r, "Incorrect username or password")

    def test_bloqueo_por_intentos(self):
        for _ in range(3):
            self.entrar("HCIS", "mal")
        r = self.entrar("HCIS", "secreta")               # correcta, pero ya está bloqueado
        self.assertContains(r, "Too many failed attempts")

    def test_modulo_requiere_login(self):
        """Las pantallas de los módulos mandan al login si no hay sesión."""
        r = self.client.get(reverse("inventario:inicio"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("cuentas:entrar"), r["Location"])

    def test_salir(self):
        self.entrar("HCIS", "secreta")
        r = self.client.post(reverse("cuentas:salir"))
        self.assertRedirects(r, reverse("cuentas:entrar"), fetch_redirect_response=False)
