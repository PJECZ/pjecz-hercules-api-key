"""
DGT Plataformas Autoridades
"""

import uuid

from pydantic import BaseModel, ConfigDict


class DgtPlataformaAutoridadOut(BaseModel):
    """Esquema para entregar plataformas-autoridades"""

    id: uuid.UUID
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    dgt_plataforma_clave: str
    dgt_plataforma_descripcion: str
    model_config = ConfigDict(from_attributes=True)


class OneDgtPlataformaAutoridadOut(BaseModel):
    """Esquema para entregar una plataforma-autoridad"""

    success: bool
    message: str
    data: DgtPlataformaAutoridadOut | None = None
