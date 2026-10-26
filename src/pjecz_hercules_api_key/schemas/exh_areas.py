"""
EXH Áreas
"""

from pydantic import BaseModel, ConfigDict


class ExhAreaOut(BaseModel):
    """Esquema para entregar áreas"""

    clave: str
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class OneExhAreaOut(BaseModel):
    """Esquema para entregar una área"""

    success: bool
    message: str
    data: ExhAreaOut | None = None
