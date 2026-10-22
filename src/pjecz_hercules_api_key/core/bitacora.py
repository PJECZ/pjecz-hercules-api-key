"""
Bitácora

Guarda en la tabla bitacoras_apis cada petición de un usuario identificado.
"""

import logging
from http import HTTPStatus

from pjecz_hercules_api_key.config.setttings import get_settings
from pjecz_hercules_api_key.core.database import session_scope
from pjecz_hercules_api_key.models.bitacoras_apis import BitacoraAPI

bitacora_logger = logging.getLogger(__name__)
settings = get_settings()


def guardar_bitacora(usuario_id: int, ruta: str, peticion: str, status_code: int) -> None:
    """Guardar un registro en la bitácora, sin interrumpir la respuesta si falla"""
    try:
        frase = HTTPStatus(status_code).phrase
    except ValueError:
        frase = ""
    try:
        with session_scope() as session:
            session.add(
                BitacoraAPI(
                    usuario_id=usuario_id,
                    api_nombre=settings.API_NOMBRE,
                    api_ruta=ruta[:512],
                    peticion=peticion,
                    respuesta_exitosa=status_code < 400,
                    respuesta_mensaje=f"{status_code} {frase}".strip()[:256],
                    respuesta_errores=[],
                    respuesta_datos=[],
                )
            )
    except Exception as error:  # pylint: disable=broad-exception-caught
        bitacora_logger.error("No se pudo guardar la bitácora: %s", error)
