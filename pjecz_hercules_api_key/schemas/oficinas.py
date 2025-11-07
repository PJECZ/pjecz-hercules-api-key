"""
Oficinas, esquemas
"""

from pydantic import BaseModel, ConfigDict


class OficinaOut(BaseModel):
    """Esquema para entregar municipios"""

    distrito_clave: str
    distrito_nombre: str
    domicilio_edificio: str
    clave: str
    descripcion: str
    descripcion_corta: str
    es_jurisdiccional: bool
    model_config = ConfigDict(from_attributes=True)


class OneOficinaOut(BaseModel):
    """Esquema para entregar un municipio"""

    success: bool
    message: str
    data: OficinaOut | None = None
