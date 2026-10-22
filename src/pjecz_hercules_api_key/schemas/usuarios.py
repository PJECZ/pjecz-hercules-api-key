"""
Usuarios
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UsuarioOut(BaseModel):
    """Esquema para entregar usuarios"""

    id: int
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    oficina_clave: str
    oficina_descripcion: str
    oficina_descripcion_corta: str
    email: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    puesto: str | None
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
    api_key_cuota_diaria: int
