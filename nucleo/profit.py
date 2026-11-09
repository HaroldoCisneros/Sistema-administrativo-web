"""
nucleo/profit.py
================

Acceso de SOLO LECTURA a las bases de Profit, compartido por todos los módulos.

Cualquier módulo que necesite datos de Profit usa estas funciones en lugar de
abrir conexiones por su cuenta. Así:
    - la conexión y sus permisos se manejan en un solo lugar,
    - todos convierten los datos igual (números, fechas vacías de Profit, etc.),
    - si algo falla en la conexión, se corrige aquí para todos.

Funciones:
    conexion_empresa(empresa)     nombre de la conexión a la base de Profit de la empresa
    consultar(sql, params, base)  ejecuta una consulta y devuelve las filas
    tasa(moneda, fecha, base)     tasa de cambio (VALOR_MONEDA de FoxPro)
    num(), txt(), fecha(), val()  conversiones de los valores que vienen de SQL

Cómo lo usa una pantalla de un módulo (la empresa elegida viene en request.empresa):
    base = conexion_empresa(request.empresa)
    filas = consultar("SELECT co_art, art_des FROM art WHERE co_art = %s", [codigo], base)

Sobre los parámetros (%s):
    Los valores NUNCA se pegan dentro del texto del SQL. Se escribe %s en su
    lugar y se pasan aparte, en "params". El driver los envía por separado,
    y así un código escaneado o escrito no puede alterar la consulta
    (protección contra "inyección SQL").
"""

import datetime as dt                      # fechas
from decimal import Decimal                # números exactos (sin errores de redondeo)

from django.db import connections          # las conexiones a las bases de datos
from django.utils import timezone          # fecha de hoy en la hora de Venezuela


def conexion_empresa(empresa):
    """
    Devuelve el nombre de la conexión a la base de Profit de una empresa
    (por ejemplo "profit_CF01") y, si es la primera vez, la registra.

    Cada empresa de Profit tiene su propia base de datos. Esa base se guarda
    en la tabla de empresas (empresas/models.py, campo base_profit), así que
    la conexión no se puede escribir fija en settings.py: se arma aquí,
    copiando la conexión principal ("default": mismo servidor, mismo usuario
    de SQL) y cambiando solo el nombre de la base.
    """
    alias = f"profit_{empresa.codigo}"                      # nombre de la conexión
    if alias not in connections.databases:                  # ¿todavía no existe?
        # dict(...) hace una copia de la conexión principal (ya trae todos los
        # valores por defecto que Django completó al arrancar) y NAME cambia la base.
        connections.databases[alias] = dict(connections.databases["default"],
                                            NAME=empresa.base_profit)
    return alias


def consultar(sql, params=(), base="usuarios"):
    """
    Ejecuta una consulta en una base de Profit y devuelve una lista de
    diccionarios, uno por fila, con los nombres de columna en minúscula.

    sql    -> la consulta, con %s donde van los valores.
    params -> los valores, en el mismo orden que los %s.
    base   -> nombre de la conexión: "usuarios" (MasterProfit) o el que
              devuelve conexion_empresa(empresa) (la base de la empresa).

    Ejemplo:
        consultar("SELECT co_art, art_des FROM art WHERE co_art = %s", ["0011407"], base)
        -> [{"co_art": "0011407", "art_des": "MARTILLO ..."}]
    """
    # connections[base] es la conexión configurada en settings.DATABASES.
    # "with" garantiza que el cursor se cierre aunque ocurra un error.
    with connections[base].cursor() as cur:
        cur.execute(sql, list(params))
        # Algunas instrucciones (SET NOCOUNT ON, EXEC de un procedimiento)
        # producen resultados vacíos antes de las filas: se saltan hasta
        # llegar a uno que tenga columnas.
        while not cur.description:
            if not cur.nextset():            # no hay más resultados
                return []
        columnas = [c[0].lower() for c in cur.description]         # nombres de columnas
        return [dict(zip(columnas, fila)) for fila in cur.fetchall()]


# ---------------------------------------------------------------------------
# Tasas de cambio
# ---------------------------------------------------------------------------
# Usa el procedimiento que ya existe en Profit: dbo.pp_valor_moneda.
#   - Busca la última tasa de la moneda hasta la fecha indicada (tabla "tasas").
#   - Si no hay, la primera posterior; si tampoco, el cambio de la tabla "moneda".
#   - Si no encuentra nada, devuelve 1.
# El procedimiento devuelve la tasa en un parámetro de salida (OUTPUT), por eso
# se declara la variable @r y luego se selecciona.
SQL_TASA = ("SET NOCOUNT ON; DECLARE @r FLOAT; "
            "EXEC [dbo].[pp_valor_moneda] %s, %s, @r OUTPUT; SELECT @r AS tasa")


def tasa(moneda, base, fecha_tasa=None):
    """
    Equivalente a VALOR_MONEDA(moneda, fecha) de FoxPro.
    moneda     -> código en Profit, por ejemplo "BS$" o "BCV".
    base       -> conexión de la empresa (la que devuelve conexion_empresa).
    fecha_tasa -> fecha de la tasa; si no se indica, hoy (hora de Venezuela).
    """
    filas = consultar(SQL_TASA, [moneda, fecha_tasa or timezone.localdate()], base)
    return num(filas[0]["tasa"], 2) if filas else 1.0


# ---------------------------------------------------------------------------
# Conversiones de los valores que devuelve SQL Server
# ---------------------------------------------------------------------------
def num(valor, decimales=5):
    """
    Número de SQL (Decimal, int, float o NULL) -> float redondeado.
    NULL se convierte en 0, igual que en FoxPro.
    Se pasa por Decimal(str(...)) para redondear sin errores de coma flotante.
    """
    if valor is None:
        return 0.0
    return float(round(Decimal(str(valor)), decimales))


def txt(valor):
    """Texto de SQL -> texto sin espacios a los lados (los campos char vienen rellenados)."""
    return str(valor or "").strip()


def fecha(valor):
    """
    Fecha o fecha-hora de SQL -> texto "AAAA-MM-DD" (formato estándar para la API).
    Profit guarda las fechas "vacías" como 01/01/1900: esas se devuelven como None.
    """
    if not valor:
        return None
    if isinstance(valor, dt.datetime):
        valor = valor.date()                 # se descarta la hora
    return None if valor.year <= 1900 else valor.isoformat()


def val(texto):
    """
    Equivalente a VAL() de FoxPro: convierte un texto en número.
    Si el texto no es un número válido, devuelve 0 (en vez de dar error).
    """
    try:
        return float(str(texto or "0").strip().replace(",", ""))
    except ValueError:
        return 0.0
