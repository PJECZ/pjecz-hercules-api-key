"""
VASPEC Digitalizaciones, esquemas
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VspDigitalizacionOut(BaseModel):
    """Esquema para entregar digitalizaciones"""

    id: int
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    expediente: str
    expediente_anio: int
    expediente_num: int
    descripcion: str | None
    archivo_uuid: uuid.UUID
    archivo: str
    url: str
    tamano: int | None = None
    tiempo: datetime | None = None
    enviado: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class OneVspDigitalizacionOut(BaseModel):
    """Esquema para entregar una digitalización"""

    success: bool
    message: str
    data: VspDigitalizacionOut | None = None
