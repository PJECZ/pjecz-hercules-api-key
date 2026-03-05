"""
Bitacoras Apis, esquemas
"""

from pydantic import BaseModel, ConfigDict


class BitacoraAPIOut(BaseModel):
    """Esquema para entregar bitacoras-apis"""

    id: int
    usuario_id: int
    usuario_email: str
    usuario_nombre: str
    api_nombre: str
    api_ruta: str
    peticion: str
    respuesta_exitosa: bool | None
    respuesta_datos: dict | None
    model_config = ConfigDict(from_attributes=True)
