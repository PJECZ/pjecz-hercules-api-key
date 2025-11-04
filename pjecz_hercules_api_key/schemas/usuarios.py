"""
Usuarios, esquemas
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UsuarioOut(BaseModel):
    """Esquema para entregar usuarios"""

    email: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    autoridad_clave: str | None = None
    autoridad_descripcion: str | None = None
    autoridad_descripcion_corta: str | None = None
    distrito_clave: str | None = None
    distrito_nombre: str | None = None
    distrito_nombre_corto: str | None = None
    puesto: str | None = None
    model_config = ConfigDict(from_attributes=True)


class OneUsuarioOut(BaseModel):
    """Esquema para entregar un usuario"""

    success: bool
    message: str
    data: UsuarioOut | None = None


class UsuarioInDB(UsuarioOut):
    """Usuario en base de datos"""

    username: str
    permissions: dict
    hashed_password: str
    disabled: bool
    api_key: str
    api_key_expiracion: datetime
