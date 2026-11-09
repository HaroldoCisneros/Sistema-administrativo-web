"""
empresas/models.py
==================

La tabla de empresas, en la base propia del sistema (SIGHEC).
Django la crea con:  python manage.py migrate

Cada fila es una empresa con la que se puede trabajar:
    codigo       código corto que el usuario escribe al entrar (ej. CF01)
    nombre       nombre completo
    rif          RIF (opcional)
    base_profit  nombre de SU base de datos en Profit (cada empresa tiene la suya)
    activa       si está en "no", no se puede elegir
    creada       fecha en que se registró (se llena sola)

Se dan de alta con el comando:
    python manage.py crear_empresa CF01 "Mi Empresa, C.A." NOMBRE_BASE_PROFIT --rif J-12345678-9
o en el panel de administración (/admin/). Más adelante también desde
Maintenance › Tables › Companies.
"""

from django.core.validators import RegexValidator    # valida un texto con un patrón
from django.db import models                          # tipos de campos de las tablas
# gettext_lazy como _: textos traducibles (nombres de campos en el panel /admin/ y errores).
from django.utils.translation import gettext_lazy as _


# Código: solo letras, números, guion y guion bajo (va en la dirección de la
# conexión a la base y en la sesión, así que no debe tener espacios ni símbolos).
validar_codigo = RegexValidator(
    r"^[A-Za-z0-9_-]+$", _("Only letters, numbers, - and _ are allowed."))

# Nombre de base de datos: solo letras, números y guion bajo (la misma regla de
# sistema/configuracion.py), porque se usa para conectarse a SQL Server.
validar_base = RegexValidator(
    r"^[A-Za-z0-9_]+$", _("Only letters, numbers and _ are allowed."))


class Empresa(models.Model):
    # unique=True: no puede haber dos empresas con el mismo código.
    codigo = models.CharField(_("code"), max_length=10, unique=True, validators=[validar_codigo])
    nombre = models.CharField(_("name"), max_length=100)
    # blank=True: se puede dejar vacío.
    rif = models.CharField(_("tax ID (RIF)"), max_length=20, blank=True)
    base_profit = models.CharField(_("Profit database"), max_length=128, validators=[validar_base],
                                   help_text=_("Name of this company's database in Profit (SQL Server)."))
    activa = models.BooleanField(_("active"), default=True)
    # auto_now_add=True: se llena sola con la fecha y hora al crear la empresa.
    creada = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        ordering = ["codigo"]                 # al listarlas, ordenadas por código
        verbose_name = _("company")              # nombre en singular (panel /admin/)
        verbose_name_plural = _("companies")     # nombre en plural

    def save(self, *args, **kwargs):
        """Antes de guardar, el código se pasa a mayúsculas y sin espacios a los lados."""
        self.codigo = (self.codigo or "").strip().upper()
        super().save(*args, **kwargs)         # guarda de verdad (lo hace Django)

    def __str__(self):
        """Cómo se muestra la empresa en el panel /admin/ y en los mensajes."""
        return f"{self.codigo} - {self.nombre}"
