"""
DGT Depósitos
"""

import uuid

from pydantic import BaseModel, ConfigDict


class DgtDepositoOut(BaseModel):
    """Esquema para entregar depósitos"""

    id: uuid.UUID
    clave: str
    descripcion: str
    proposito: str
    model_config = ConfigDict(from_attributes=True)


class OneDgtDepositoOut(BaseModel):
    """Esquema para entregar un depósitos"""

    success: bool
    message: str
    data: DgtDepositoOut | None = None
