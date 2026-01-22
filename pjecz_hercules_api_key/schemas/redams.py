"""
REDAM, esquemas
"""

from datetime import date

from pydantic import BaseModel, ConfigDict


class RedamOut(BaseModel):
    """Esquema para entregar REDAMs"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    nombre: str
    expediente: str
    fecha: date
    observaciones: str
    model_config = ConfigDict(from_attributes=True)
