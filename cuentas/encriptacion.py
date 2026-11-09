"""
cuentas/encriptacion.py
=======================

Encriptación de claves de Profit Plus, traducida de la función de Visual FoxPro:

    FUNCTION ENCRIPT                       FUNCTION FUN
    PARAMETER PKEY                         PARAMETER CAR
    KEY_ENCRIPT = " "                      RETURN( CHR((( ASC(CAR) +17)*11)%255) )
    FOR I = 1 TO LEN(PKEY)                 ENDFUNC
        KEY_ENCRIPT = KEY_ENCRIPT+FUN(SUBSTR(PKEY,I,1))
    NEXT
    RETURN(SUBSTR(KEY_ENCRIPT,2,LEN(KEY_ENCRIPT) - 1))

Es decir: cada carácter de la clave se reemplaza por
    CHR( ((código del carácter + 17) * 11) módulo 255 )
El espacio inicial de KEY_ENCRIPT se quita al final, así que no afecta.

ASC() de FoxPro da el código del carácter en la página de códigos de Windows
(Windows-1252); por eso en Python se usa "cp1252".
"""

import hmac      # compare_digest: compara sin revelar por tiempo cuántos caracteres coinciden

# El campo employee.password es char(15): la clave guardada ocupa como máximo 15.
LARGO_CAMPO = 15


def encriptar(clave: str) -> bytes:
    """
    Clave en texto -> bytes tal como Profit los guarda (sin el relleno de espacios).
    Ejemplo: "A" (código 65) -> ((65 + 17) * 11) % 255 = 137 -> b'\\x89'
    """
    # clave.encode("cp1252") da los códigos de cada carácter (como ASC de FoxPro).
    return bytes(((c + 17) * 11) % 255 for c in clave.encode("cp1252"))


def clave_coincide(clave: str, guardada: bytes, mayusculas: bool = False) -> bool:
    """
    Compara la clave que escribió el usuario con la guardada en employee.password.

    clave      -> lo que escribió el usuario.
    guardada   -> bytes crudos del campo (se leen con CAST(password AS VARBINARY(15))
                  para que SQL no los convierta a texto y altere caracteres especiales).
    mayusculas -> True si Profit guarda las claves en mayúsculas
                  (se configura en config.xml <clave_mayusculas>).
    """
    if not clave or guardada is None:
        return False
    if mayusculas:
        clave = clave.upper()
    try:
        calculada = encriptar(clave)[:LARGO_CAMPO]
    except UnicodeEncodeError:
        # Carácter que no existe en Windows-1252 (por ejemplo un emoji):
        # Profit no pudo haberlo guardado, así que la clave no coincide.
        return False
    # El campo char(15) viene rellenado con espacios a la derecha: se quitan de
    # los dos lados antes de comparar. (El carácter "}" se encripta como espacio;
    # como se quita igual en ambos lados, la comparación sigue siendo correcta.)
    return hmac.compare_digest(calculada.rstrip(b" "), bytes(guardada).rstrip(b" "))
