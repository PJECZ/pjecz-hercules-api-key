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
    rag_fue_analizado_tiempo: datetime | None = None
    rag_fue_sintetizado_tiempo: datetime | None = None
    rag_fue_categorizado_tiempo: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ListaDeAcuerdoRAGOut(ListaDeAcuerdoOut):
    """Agregar los campos RAG para cuando se entrega una lista de acuerdos"""

    rag_analisis: dict | None = None
    rag_sintesis: dict | None = None
    rag_categorias: dict | None = None


class OneListaDeAcuerdoOut(BaseModel):
    """Esquema para entregar una lista de acuerdos"""

    success: bool
    message: str
    data: ListaDeAcuerdoRAGOut | None = None
