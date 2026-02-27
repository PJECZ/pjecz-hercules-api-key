"""
Arc Juzgados Extintos, esquemas
"""

from pydantic import BaseModel, ConfigDict


class ArcJuzgadoExtintoOut(BaseModel):
    """Esquema para entregar juzgados extintos"""

    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    clave: str
    descripcion: str
    descripcion_corta: str
    model_config = ConfigDict(from_attributes=True)


class OneArcJuzgadoExtintoOut(BaseModel):
    """Esquema para entregar un juzgado extinto"""

    success: bool
    message: str
    data: ArcJuzgadoExtintoOut | None = None
