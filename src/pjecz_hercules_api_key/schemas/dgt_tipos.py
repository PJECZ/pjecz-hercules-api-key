"""
DGT Tipos
"""

import uuid

from pydantic import BaseModel, ConfigDict


class DgtTipoOut(BaseModel):
    """Esquema para entregar tipos"""

    id: uuid.UUID
    clave: str
    descripcion: str
    model_config = ConfigDict(from_attributes=True)


class OneDgtTipoOut(BaseModel):
    """Esquema para entregar un tipo"""

    success: bool
    message: str
    data: DgtTipoOut | None = None
