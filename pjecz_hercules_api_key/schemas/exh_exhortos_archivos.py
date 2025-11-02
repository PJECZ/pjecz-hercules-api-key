"""
Exh Exhortos Archivos, esquemas de pydantic
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExhExhortoArchivoOut(BaseModel):
    """Esquema para entregar exhortos Archivos"""

    id: int
    nombre_archivo: str
    hash_sha1: str | None = None
    hash_sha256: str | None = None
    tipo_documento: int
    url: str
    tamano: int | None = None
    fecha_hora_recepcion: datetime
    estado: str
    model_config = ConfigDict(from_attributes=True)


class ExhExhortoArchivoIn(BaseModel):
    """Esquema para recibir exhortos Archivo"""

    nombre_archivo: str
    tipo_documento: int
    url: str
    tamano: int | None = None
