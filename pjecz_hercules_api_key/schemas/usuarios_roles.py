"""
Usuarios-Roles, esquemas
"""

from pydantic import BaseModel, ConfigDict


class UsuarioRolOut(BaseModel):
    """Esquema para entregar usuarios-roles"""

    id: int
    rol_nombre: str
    usuario_nombre: str
    descripcion: str
    model_config = ConfigDict(from_attributes=True)


class OneUsuarioRolOut(BaseModel):
    """Esquema para entregar un usuario-rol"""

    success: bool
    message: str
    data: UsuarioRolOut | None = None
