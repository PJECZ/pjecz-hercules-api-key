"""
Arc Remesas, esquemas
"""

from pydantic import BaseModel, ConfigDict


class ArcRemesaOut(BaseModel):
    """Esquema para entregar remesas"""

    id: int
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    num_oficio: str
    estado: str
    model_config = ConfigDict(from_attributes=True)


class OneArcRemesaOut(BaseModel):
    """Esquema para entregar una remesa"""

    success: bool
    message: str
    data: ArcRemesaOut | None = None
