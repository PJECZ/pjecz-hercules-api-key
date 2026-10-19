"""
Validation

Funciones para validar y normalizar los parámetros de consulta.
Lanzan HTTPException 422 cuando un parámetro no pasa la validación.
Si un texto queda vacío después de normalizar, entregan una cadena vacía para que el filtro se ignore.
"""

import re
from datetime import date

from fastapi import HTTPException, status
from unidecode import unidecode

CLAVE_REGEXP = r"^[A-Z0-9_-]+$"
CURP_REGEXP = r"^[a-zA-Z]{4}\d{6}[a-zA-Z]{6}[A-Z0-9]{2}$"
EMAIL_REGEXP = r"^[\w.-]+@[\w.-]+\.\w+$"
EXPEDIENTE_REGEXP = r"^\d{1,5}/(19|20)\d{2}(-[A-Z0-9]+)?$"
CARACTERES_CONSERVADOS = "ÑÜ"


def _raise_422(detail: str) -> None:
    """Lanzar HTTPException 422"""
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)


def safe_string(texto: str, max_len: int = 256) -> str:
    """Quitar espacios sobrantes, convertir a mayúsculas y quitar acentos, conservando Ñ y Ü"""
    texto = re.sub(r"\s+", " ", texto.strip()).upper()
    texto = "".join(c if c in CARACTERES_CONSERVADOS else unidecode(c) for c in texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:max_len].strip()


def safe_clave(clave: str, max_len: int = 16) -> str:
    """Validar una clave"""
    clave = safe_string(clave, max_len)
    if clave == "":
        return ""
    if re.match(CLAVE_REGEXP, clave) is None:
        _raise_422("La clave no es válida")
    return clave


def safe_curp(texto: str) -> str:
    """Validar un CURP"""
    texto = texto.strip()
    if texto == "":
        return ""
    if re.match(CURP_REGEXP, texto) is None:
        _raise_422("El CURP no es válido")
    return texto


def safe_email(texto: str) -> str:
    """Validar un correo electrónico"""
    texto = texto.strip()
    if texto == "":
        return ""
    if re.match(EMAIL_REGEXP, texto) is None:
        _raise_422("El correo electrónico no es válido")
    return texto


def safe_expediente(expediente: str) -> str:
    """Validar un expediente y quitar los ceros a la izquierda del número"""
    expediente = safe_string(expediente)
    if expediente == "":
        return ""
    if re.match(EXPEDIENTE_REGEXP, expediente) is None:
        _raise_422("El expediente no es válido")
    numero, resto = expediente.split("/", 1)
    return f"{int(numero)}/{resto}"


def validate_fechas(fecha: date | None, fecha_desde: date | None, fecha_hasta: date | None) -> None:
    """Validar la combinación de fecha con el rango de fechas"""
    if fecha is not None and (fecha_desde is not None or fecha_hasta is not None):
        _raise_422("No se puede combinar fecha con fecha_desde o fecha_hasta")
    if fecha_desde is not None and fecha_hasta is not None and fecha_desde > fecha_hasta:
        _raise_422("La fecha_desde no puede ser posterior a la fecha_hasta")
