"""
Listas de Acuerdos, esquemas
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ListaDeAcuerdoOut(BaseModel):
    """Esquema para entregar listas de acuerdos"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    fecha: date
    descripcion: str
    model_config = ConfigDict(from_attributes=True)


class OneListaDeAcuerdoOut(BaseModel):
    """Esquema para entregar una lista de acuerdos"""

    success: bool
    message: str
    data: ListaDeAcuerdoOut | None = None
