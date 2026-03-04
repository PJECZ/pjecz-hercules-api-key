"""
Bitacoras Apis, esquemas
"""

from pydantic import BaseModel, ConfigDict


class BitacoraAPIOut(BaseModel):
    """Esquema para entregar bitacoras-apis"""

    id: int
    usuario_id: int
    api_nombre: str
    api_ruta: str
    peticion: str
    respuesta_exitosa: bool | None
    model_config = ConfigDict(from_attributes=True)
