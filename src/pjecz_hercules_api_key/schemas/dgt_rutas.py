"""
DGT Rutas
"""

import uuid

from pydantic import BaseModel, ConfigDict


class DgtRutaOut(BaseModel):
    """Esquema para entregar rutas"""

    id: uuid.UUID
    dgt_deposito_descripcion: str
    dgt_deposito_proposito: str
    dgt_tipo_clave: str
    dgt_tipo_descripcion: str
    clave: str
    autoridad_clave: str
    directorio: str
    model_config = ConfigDict(from_attributes=True)


class OneDgtRutaOut(BaseModel):
    """Esquema para entregar una ruta"""

    success: bool
    message: str
    data: DgtRutaOut | None = None
