"""
Domicilios, esquemas
"""

from pydantic import BaseModel, ConfigDict


class DomicilioOut(BaseModel):
    """Esquema para entregar Domicilios"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    edificio: str
    estado: str
    municipio: str
    calle: str
    num_ext: str
    num_int: str
    colonia: str
    cp: int
    completo: str
    model_config = ConfigDict(from_attributes=True)


class OneDomicilioOut(BaseModel):
    """Esquema para entregar un Domicilio"""

    success: bool
    message: str
    data: DomicilioOut | None = None
