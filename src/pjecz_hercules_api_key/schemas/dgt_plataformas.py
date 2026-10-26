"""
DGT Plataformas
"""

import uuid

from pydantic import BaseModel, ConfigDict


class DgtPlataformaOut(BaseModel):
    """Esquema para entregar plataformas"""

    id: uuid.UUID
    clave: str
    descripcion: str
    model_config = ConfigDict(from_attributes=True)


class OneDgtPlataformaOut(BaseModel):
    """Esquema para entregar una plataforma"""

    success: bool
    message: str
    data: DgtPlataformaOut | None = None
