"""
empresas/management/commands/crear_empresa.py
=============================================

Comando para dar de alta (o actualizar) una empresa desde la CMD.

Uso (dentro de la carpeta del proyecto):
    python manage.py crear_empresa CODIGO "Nombre" BASE_PROFIT [--rif RIF] [--inactiva]

Ejemplos:
    python manage.py crear_empresa CF01 "Mi Empresa, C.A." MI_EMPRESA --rif J-12345678-9
    python manage.py crear_empresa CF01 "Mi Empresa, C.A. (Principal)" MI_EMPRESA   (actualiza el nombre)

Si el código ya existe, actualiza sus datos en vez de dar error.
"""

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from empresas.models import Empresa


class Command(BaseCommand):
    help = "Creates or updates a company (code, name and Profit database)."

    def add_arguments(self, parser):
        """Los datos que se escriben después de "crear_empresa"."""
        parser.add_argument("codigo")                         # obligatorio
        parser.add_argument("nombre")                         # obligatorio
        parser.add_argument("base_profit")                    # obligatorio
        parser.add_argument("--rif", default="")              # opcional
        parser.add_argument("--inactiva", action="store_true")  # opcional: la crea desactivada

    def handle(self, *args, **op):
        """Lo que hace el comando."""
        codigo = op["codigo"].strip().upper()
        # Busca la empresa por código; si no existe, prepara una nueva (todavía sin guardar).
        empresa = Empresa.objects.filter(codigo=codigo).first() or Empresa(codigo=codigo)
        nueva = empresa.pk is None                            # sin pk = todavía no está en la base
        empresa.nombre = op["nombre"].strip()
        empresa.base_profit = op["base_profit"].strip()
        empresa.rif = op["rif"].strip()
        empresa.activa = not op["inactiva"]
        try:
            # full_clean valida los campos (código y base solo con caracteres permitidos, etc.).
            # exclude=["codigo"] cuando ya existe, para que no se queje de "código repetido".
            empresa.full_clean(exclude=[] if nueva else ["codigo"])
        except ValidationError as e:
            # Muestra cada error en una línea: "base_profit: Only letters, numbers and _ ..."
            raise CommandError("\n".join(f"{campo}: {', '.join(msjs)}"
                                         for campo, msjs in e.message_dict.items()))
        empresa.save()
        accion = "created" if nueva else "updated"
        self.stdout.write(self.style.SUCCESS(f"Company {empresa} {accion}."))
