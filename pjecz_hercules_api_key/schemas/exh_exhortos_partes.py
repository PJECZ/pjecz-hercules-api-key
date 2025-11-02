"""
Exh Exhortos Partes, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict


class ExhExhortoParteOut(BaseModel):
    """Esquema para entregar exhortos Partes"""

    id: int
    nombre: str
    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    genero: str
    es_persona_moral: bool
    tipo_parte: int
    tipo_parte_nombre: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ExhExhortoParteIn(BaseModel):
    """Esquema para recibir exhortos Parte"""

    nombre: str
    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    genero: str | None = None
    es_persona_moral: bool
    tipo_parte: int
    tipo_parte_nombre: str | None = None
