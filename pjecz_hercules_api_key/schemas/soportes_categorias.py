"""
Soportes Categorias, esquemas
"""

from pydantic import BaseModel, ConfigDict


class SoporteCategoriaOut(BaseModel):
    """Esquema para entregar Soportes Categorias"""

    id: int
    nombre: str
    departamento: str
    model_config = ConfigDict(from_attributes=True)


class OneSoporteCategoriaOut(BaseModel):
    """Esquema para entregar un Soporte Categoria"""

    success: bool
    message: str
    data: SoporteCategoriaOut | None = None
