"""
Safe string
"""

import re
from datetime import date

from unidecode import unidecode

CURP_REGEXP = r"^[A-Z]{4}\d{6}[A-Z]{6}[A-Z0-9]{2}$"
EMAIL_REGEXP = r"^[\w.-]+@[\w.-]+\.\w+$"
PASSWORD_REGEXP = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,24}$"
TELEFONO_REGEXP = r"^[1-9]\d{9}$"
URL_REGEXP = r"^(https?:\/\/)[0-9a-z-_]*(\.[0-9a-z-_]+)*(\.[a-z]+)+(:(\d+))?(\/[0-9a-z%-_]*)*?\/?$"


def extract_expediente_anio(input_str: str) -> int:
    """Extraer el anio AAAA del expediente NN/AAAA-XX como un entero"""
    # Validar que comience con un numero/anio
    inicio_str = re.match(r"^\d+\/[12]\d\d\d", input_str)
    if inicio_str is None:
        return 0
    # Entregar el anio como entero
    return int(inicio_str.group(0).split("/")[1])


def extract_expediente_num(input_str: str) -> int:
    """Extraer el numero NN del expediente NN/AAAA-XX como un entero"""
    # Validar que comience con un numero/anio
    inicio_str = re.match(r"^\d+\/[12]\d\d\d", input_str)
    if inicio_str is None:
        return 0
    # Entregar el numero como entero
    return int(inicio_str.group(0).split("/")[0])


def safe_clave(input_str):
    """Safe clave"""
    if not isinstance(input_str, str):
        raise ValueError("La clave esta vacia")
    new_string = input_str.strip().upper()
    regexp = re.compile("^[A-Z0-9-]{2,16}$")
    if regexp.match(new_string) is None:
        raise ValueError("La clave es incorrecta")
    return new_string


def safe_curp(input_str):
    """Safe CURP"""
    if not isinstance(input_str, str):
        raise ValueError("CURP no es texto")
    removed_spaces = re.sub(r"\s", "", input_str)
    removed_simbols = re.sub(r"[()\[\]:/.-]+", "", removed_spaces)
    final = unidecode(removed_simbols.upper())
    if re.fullmatch(CURP_REGEXP, final) is None:
        raise ValueError("CURP es incorrecto")
    return final


def safe_email(input_str, search_fragment=False) -> str:
    """Safe email"""
    if not isinstance(input_str, str) or input_str.strip() == "":
        raise ValueError("Email es incorrecto")
    final = input_str.strip().lower()
    if search_fragment:
        if re.match(r"^[\w.-]*@*[\w.-]*\.*\w*$", final) is None:
            return ""
        return final
    regexp = re.compile(EMAIL_REGEXP)
    if regexp.match(final) is None:
        raise ValueError("Email es incorrecto")
    return final


def safe_expediente(input_str):
    """Safe expediente"""
    if not isinstance(input_str, str) or input_str.strip() == "":
        raise ValueError("Expediente es incorrecto")
    elementos = re.sub(r"[^a-zA-Z0-9]+", "|", unidecode(input_str)).split("|")
    try:
        numero = int(elementos[0])
        anio = int(elementos[1])
    except (IndexError, ValueError) as error:
        raise error
    if anio < 1900 or anio > date.today().year:
        raise ValueError
    extra_1 = ""
    if len(elementos) >= 3:
        extra_1 = "-" + elementos[2].upper()
    extra_2 = ""
    if len(elementos) >= 4:
        extra_2 = "-" + elementos[3].upper()
    limpio = f"{str(numero)}/{str(anio)}{extra_1}{extra_2}"
    if len(limpio) > 16:
        raise ValueError
    return limpio


def safe_string(input_str, max_len=250):
    """Safe string"""
    if not isinstance(input_str, str):
        return ""
    new_string = re.sub(r"[^a-zA-Z0-9,/-]+", " ", unidecode(input_str))
    removed_multiple_spaces = re.sub(r"\s+", " ", new_string)
    final = removed_multiple_spaces.strip().upper()
    return (final[:max_len] + "...") if len(final) > max_len else final


def safe_telefono(input_str):
    """Safe telefono"""
    if not isinstance(input_str, str):
        raise ValueError("Telefono no es texto")
    solo_numeros = re.sub(r"[^0-9]+", "", unidecode(input_str))
    if re.match(TELEFONO_REGEXP, solo_numeros) is None:
        raise ValueError("Telefono está incompleto")
    return solo_numeros


def safe_url(input_str):
    """Safe URL"""
    if not isinstance(input_str, str) or input_str.strip() == "":
        return ""
    input_str = input_str.strip()
    if re.match(URL_REGEXP, input_str) is None:
        return ""
    return input_str
