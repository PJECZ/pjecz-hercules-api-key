"""
Glosas
"""

from datetime import date

from pydantic import BaseModel, ConfigDict


class GlosaOut(BaseModel):
    """Esquema para entregar glosas"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    fecha: date
    tipo_juicio: str
    descripcion: str
    expediente: str
    model_config = ConfigDict(from_attributes=True)


class OneGlosaOut(BaseModel):
    """Esquema para entregar una glosa"""

    success: bool
    message: str
    data: GlosaOut | None = None
