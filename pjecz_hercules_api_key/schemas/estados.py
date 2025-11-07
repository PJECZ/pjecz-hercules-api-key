"""
Estados, esquemas
"""

from pydantic import BaseModel, ConfigDict


class EstadoOut(BaseModel):
    """Esquema para entregar Estados"""

    clave: str
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class OneEstadoOut(BaseModel):
    """Esquema para entregar un Estado"""

    success: bool
    message: str
    data: EstadoOut | None = None
