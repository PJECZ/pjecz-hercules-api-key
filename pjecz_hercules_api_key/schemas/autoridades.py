"""
Autoridades, esquemas
"""

from pydantic import BaseModel, ConfigDict


class AutoridadOut(BaseModel):
    """Esquema para entregar autoridades"""

    clave: str
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    materia_clave: str
    materia_nombre: str
    municipio_clave: str
    municipio_nombre: str
    descripcion: str
    descripcion_corta: str
    es_extinto: bool
    es_cemasc: bool
    es_defensoria: bool
    es_jurisdiccional: bool
    es_notaria: bool
    es_organo_especializado: bool
    organo_jurisdiccional: str
    model_config = ConfigDict(from_attributes=True)


class OneAutoridadOut(BaseModel):
    """Esquema para entregar una autoridad"""

    success: bool
    message: str
    data: AutoridadOut | None = None
