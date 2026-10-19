"""
DGT Plataformas Endpoints
"""

import uuid

from pydantic import BaseModel, ConfigDict


class DgtPlataformaEndpointOut(BaseModel):
    """Esquema para entregar plataformas-endpoints"""

    id: uuid.UUID
    dgt_plataforma_descripcion: str
    descripcion: str
    ruta: str
    proposito: str
    metodo: str
    payload_muestra: dict
    model_config = ConfigDict(from_attributes=True)


class OneDgtPlataformaEndpointOut(BaseModel):
    """Esquema para entregar una plataforma-endpoint"""

    success: bool
    message: str
    data: DgtPlataformaEndpointOut | None = None
