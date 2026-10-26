"""
EXH Exhortos Partes
"""

from pydantic import BaseModel, ConfigDict


class ExhExhortoParteOut(BaseModel):
    """Esquema para entregar exhortos-partes"""

    id: int
    nombre: str
    apellido_paterno: str | None = None
    apellido_materno: str | None = None
    genero: str
    es_persona_moral: bool
    tipo_parte: int
    tipo_parte_nombre: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OneExhExhortoParteOut(BaseModel):
    """Esquema para entregar un exhorto-parte"""

    success: bool
    message: str
    data: ExhExhortoParteOut | None = None
