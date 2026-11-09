"""
nucleo/management/commands/compilar_idiomas.py
==============================================

Compila las traducciones: convierte cada archivo de texto .po (el que se
edita) en su .mo (el que lee Django, más rápido).

Uso (en la CMD, dentro de la carpeta del proyecto):
    python manage.py compilar_idiomas

¿Cuándo usarlo?
    Cada vez que se cambie o se agregue una traducción en algún
    <modulo>/locale/<idioma>/LC_MESSAGES/django.po. Después hay que
    reiniciar el sistema (iniciar.py) para que tome los cambios.

¿Por qué un comando propio?
    Django trae "compilemessages", pero necesita instalar las herramientas
    GNU gettext en Windows. Este comando hace lo mismo solo con Python, así
    no hay que instalar nada en el servidor.

Formato de un archivo .po (lo que se edita):
    # comentario
    msgid "Customers"        <- el texto en inglés, tal como está en el código
    msgstr "Clientes"        <- su traducción
    Si msgstr queda vacío (""), se muestra el texto en inglés.
"""

import ast          # ast.literal_eval: convierte "texto entre comillas" de forma segura
import struct       # arma los números binarios del archivo .mo
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


def leer_po(ruta):
    """
    Lee un archivo .po y devuelve un diccionario {texto_original: traducción}.
    Se saltan las entradas sin traducción y las marcadas "fuzzy" (dudosas).
    La entrada con msgid vacío es la cabecera (dice que el archivo es UTF-8).
    """
    traducciones = {}
    msgid = msgstr = None          # la entrada que se está leyendo
    campo = None                   # qué se está leyendo: "msgid" o "msgstr"
    dudosa = False                 # ¿la entrada que se está leyendo es fuzzy?
    proxima_dudosa = False         # ¿apareció "#, fuzzy" antes del próximo msgid?

    def guardar():
        """Guarda la entrada leída si tiene traducción (la cabecera siempre)."""
        if msgid is not None and msgstr and (msgid == "" or not dudosa):
            traducciones[msgid] = msgstr

    for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), start=1):
        linea = linea.strip()
        try:
            if linea.startswith("#,") and "fuzzy" in linea:
                proxima_dudosa = True                          # "#, fuzzy": la próxima no se usa
            elif linea.startswith("#") or not linea:
                continue                                       # comentario o línea vacía
            elif linea.startswith("msgid "):
                guardar()                                      # termina la entrada anterior
                msgid, msgstr, campo = ast.literal_eval(linea[6:]), None, "msgid"
                dudosa, proxima_dudosa = proxima_dudosa, False
            elif linea.startswith("msgstr "):
                msgstr, campo = ast.literal_eval(linea[7:]), "msgstr"
            elif linea.startswith('"'):
                # Continuación en varias líneas: "texto" "más texto" se pegan.
                if campo == "msgid":
                    msgid += ast.literal_eval(linea)
                elif campo == "msgstr":
                    msgstr += ast.literal_eval(linea)
            else:
                raise ValueError("línea no reconocida")
        except (ValueError, SyntaxError) as e:
            raise CommandError(f"{ruta}, línea {n}: {e}: {linea}")
    guardar()                                                  # la última entrada
    return traducciones


def escribir_mo(traducciones, ruta):
    """
    Escribe el archivo .mo (formato binario estándar de GNU gettext):
      - una cabecera con 7 números,
      - una tabla con largo y posición de cada texto original,
      - otra tabla igual para las traducciones,
      - y los textos mismos, en UTF-8, terminados en un byte 0.
    Los textos van ordenados (así los busca el lector).
    """
    claves = sorted(traducciones)                              # orden exigido por el formato
    originales = [k.encode("utf-8") for k in claves]
    traducidos = [traducciones[k].encode("utf-8") for k in claves]
    n = len(claves)

    inicio_tablas = 7 * 4                                      # la cabecera ocupa 7 números de 4 bytes
    tabla_trad = inicio_tablas + n * 8                         # cada fila de tabla: largo + posición
    inicio_textos = tabla_trad + n * 8

    tabla1, tabla2, textos = [], [], b""
    for texto in originales:                                   # primero todos los originales
        tabla1 += [len(texto), inicio_textos + len(textos)]
        textos += texto + b"\0"
    for texto in traducidos:                                   # luego todas las traducciones
        tabla2 += [len(texto), inicio_textos + len(textos)]
        textos += texto + b"\0"

    cabecera = struct.pack(
        "<7I",                                                 # 7 enteros sin signo, little-endian
        0x950412DE,                                            # número "mágico" que identifica un .mo
        0,                                                     # versión del formato
        n,                                                     # cantidad de textos
        inicio_tablas,                                         # dónde empieza la tabla de originales
        tabla_trad,                                            # dónde empieza la de traducciones
        0, 0)                                                  # tabla hash (opcional, no se usa)
    datos = cabecera + struct.pack(f"<{2 * n}I", *tabla1) + struct.pack(f"<{2 * n}I", *tabla2) + textos
    ruta.write_bytes(datos)


class Command(BaseCommand):
    help = "Compiles the translation files (.po -> .mo) of every module."

    def handle(self, *args, **opciones):
        raiz = Path(settings.BASE_DIR)
        archivos = sorted(raiz.glob("*/locale/*/LC_MESSAGES/django.po"))   # todos los módulos
        if not archivos:
            raise CommandError("No se encontraron archivos .po")
        for po in archivos:
            traducciones = leer_po(po)
            if "" not in traducciones:
                raise CommandError(f"{po}: falta la cabecera (msgid \"\") con el charset UTF-8")
            escribir_mo(traducciones, po.with_suffix(".mo"))
            self.stdout.write(f"  {po.relative_to(raiz)}  ({len(traducciones) - 1} textos)")
        self.stdout.write(self.style.SUCCESS("Listo. Reinicie el sistema para ver los cambios."))
