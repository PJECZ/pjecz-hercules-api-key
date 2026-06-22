"""
Edictos, esquemas
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EdictoOut(BaseModel):
    """Esquema para entregar edictos"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    fecha: date
    descripcion: str
    expediente: str
    numero_publicacion: str
    es_declaracion_de_ausencia: bool = False
    model_config = ConfigDict(from_attributes=True)


class OneEdictoOut(BaseModel):
    """Esquema para entregar un edicto"""

    success: bool
    message: str
    data: EdictoOut | None = None
