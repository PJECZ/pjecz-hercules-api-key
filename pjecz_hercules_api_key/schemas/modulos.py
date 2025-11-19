"""
Modulos, esquemas
"""

from pydantic import BaseModel, ConfigDict


class ModuloOut(BaseModel):
    """Esquema para entregar modulos"""

    id: int
    nombre_corto: str
    nombre: str
    icono: str
    ruta: str
    en_navegacion: bool
    model_config = ConfigDict(from_attributes=True)


class OneModuloOut(BaseModel):
    """Esquema para entregar un modulo"""

    success: bool
    message: str
    data: ModuloOut | None = None
