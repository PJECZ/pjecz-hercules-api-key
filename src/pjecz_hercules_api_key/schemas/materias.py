"""
Materias
"""

from pydantic import BaseModel, ConfigDict


class MateriaOut(BaseModel):
    """Esquema para entregar materias"""

    clave: str
    nombre: str
    descripcion: str
    en_sentencias: bool
    model_config = ConfigDict(from_attributes=True)


class OneMateriaOut(BaseModel):
    """Esquema para entregar una materia"""

    success: bool
    message: str
    data: MateriaOut | None = None
