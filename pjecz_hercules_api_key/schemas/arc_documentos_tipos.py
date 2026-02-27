"""
Arc Documentos Tipos, esquemas
"""

from pydantic import BaseModel, ConfigDict


class ArcDocumentoTipoOut(BaseModel):
    """Esquema para entregar tipos"""

    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class OneArcDocumentoTipoOut(BaseModel):
    """Esquema para entregar un tipo"""

    success: bool
    message: str
    data: ArDocumentoTipoOut | None = None
