"""
EXH Tipos Diligencias
"""

from pydantic import BaseModel, ConfigDict


class ExhTipoDiligenciaOut(BaseModel):
    """Esquema para entregar tipos diligencias"""

    clave: str
    descripcion: str
    model_config = ConfigDict(from_attributes=True)


class OneExhTipoDiligenciaOut(BaseModel):
    """Esquema para entregar una tipo diligencia"""

    success: bool
    message: str
    data: ExhTipoDiligenciaOut | None = None
