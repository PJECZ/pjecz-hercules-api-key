"""
Permisos, esquemas
"""

from pydantic import BaseModel, ConfigDict


class PermisoOut(BaseModel):
    """Esquema para entregar permisos"""

    id: int
    rol_nombre: str
    modulo_nombre: str
    nombre: str
    nivel: int
    model_config = ConfigDict(from_attributes=True)


class OnePermisoOut(BaseModel):
    """Esquema para entregar un permiso"""

    success: bool
    message: str
    data: PermisoOut | None = None
