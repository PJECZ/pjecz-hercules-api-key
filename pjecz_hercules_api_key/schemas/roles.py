"""
Roles, esquemas
"""

from pydantic import BaseModel, ConfigDict


class RolOut(BaseModel):
    """Esquema para entregar roles"""

    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class OneRolOut(BaseModel):
    """Esquema para entregar un rol"""

    success: bool
    message: str
    data: RolOut | None = None
