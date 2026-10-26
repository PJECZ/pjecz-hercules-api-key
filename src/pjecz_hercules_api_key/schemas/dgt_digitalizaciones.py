"""
DGT Digitalizaciones
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DgtDigitalizacionOut(BaseModel):
    """Esquema para entregar digitalizaciones"""

    id: uuid.UUID
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    dgt_ruta_clave: str
    archivo_nombre: str
    archivo_url: str
    archivo_public_url: str
    archivo_md5: str
    archivo_crc32c: str
    archivo_actualizado: datetime
    archivo_tamano: int
    expediente: str | None = None
    expediente_anio: int | None = None
    expediente_num: int | None = None
    descripcion: str | None = None
    es_anomalo: bool
    ultimo_evento: str
    ultimo_evento_creado: datetime
    model_config = ConfigDict(from_attributes=True)


class OneDgtDigitalizacionOut(BaseModel):
    """Esquema para entregar una digitalizacion"""

    success: bool
    message: str
    data: DgtDigitalizacionOut | None = None
