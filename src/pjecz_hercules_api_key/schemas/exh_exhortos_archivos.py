"""
EXH Exhortos Archivos
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExhExhortoArchivoOut(BaseModel):
    """Esquema para entregar exhortos-archivos"""

    id: int
    nombre_archivo: str
    hash_sha1: str | None = None
    hash_sha256: str | None = None
    tipo_documento: int
    url: str | None = None
    tamano: int | None = None
    fecha_hora_recepcion: datetime
    estado: str
    model_config = ConfigDict(from_attributes=True)


class OneExhExhortoArchivoOut(BaseModel):
    """Esquema para entregar un exhorto-archivo"""

    success: bool
    message: str
    data: ExhExhortoArchivoOut | None = None
