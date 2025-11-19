"""
Municipios, esquemas
"""

from pydantic import BaseModel, ConfigDict


class MunicipioOut(BaseModel):
    """Esquema para entregar municipios"""

    clave: str
    nombre: str
    estado_clave: str
    estado_nombre: str
    model_config = ConfigDict(from_attributes=True)


class OneMunicipioOut(BaseModel):
    """Esquema para entregar un municipio"""

    success: bool
    message: str
    data: MunicipioOut | None = None
