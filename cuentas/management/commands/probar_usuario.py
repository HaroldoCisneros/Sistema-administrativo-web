"""
cuentas/management/commands/probar_usuario.py
=============================================

Comando para comprobar si una clave coincide con la guardada en Profit,
SIN iniciar sesión. Sirve para confirmar que la encriptación está bien
configurada (por ejemplo, si Profit guarda las claves en mayúsculas).

Uso (en la CMD, dentro de la carpeta del proyecto):
    python manage.py probar_usuario CODIGO

Pide la clave sin mostrarla en pantalla y dice si coincide:
    - tal como se escribió, o
    - solo en MAYÚSCULAS (entonces hay que poner <clave_mayusculas>si</clave_mayusculas>), o
    - no coincide.
"""

from getpass import getpass          # pide la clave sin mostrarla

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from cuentas.backends import leer_empleado
from cuentas.encriptacion import clave_coincide


class Command(BaseCommand):
    help = "Checks a Profit user's password (does not sign in)."

    def add_arguments(self, parser):
        parser.add_argument("codigo")                   # el código de usuario de Profit

    def handle(self, *args, **opciones):
        codigo = opciones["codigo"].strip().upper()
        empleado = leer_empleado(codigo)
        if not empleado:
            raise CommandError(f"El usuario {codigo} no existe en "
                               f"{settings.USUARIOS['base']}.dbo.{settings.USUARIOS['tabla']}")
        self.stdout.write(f"Usuario: {empleado['codigo']} - {empleado['nombre']}")
        self.stdout.write(f"Activo: {'sí' if empleado['activo'] else 'NO'}   "
                          f"Estado: {empleado['estado'] or '(vacío)'}")
        clave = getpass("Clave: ")
        tal_cual = clave_coincide(clave, empleado["clave"], mayusculas=False)
        en_mayus = clave_coincide(clave, empleado["clave"], mayusculas=True)
        if tal_cual:
            self.stdout.write(self.style.SUCCESS("La clave coincide tal como se escribió."))
        elif en_mayus:
            self.stdout.write(self.style.WARNING(
                "La clave coincide solo en MAYÚSCULAS: ponga "
                "<clave_mayusculas>si</clave_mayusculas> en config.xml."))
        else:
            self.stdout.write(self.style.ERROR("La clave NO coincide."))
