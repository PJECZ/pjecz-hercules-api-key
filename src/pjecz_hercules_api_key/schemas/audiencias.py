"""
Audiencias
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AudienciaOut(BaseModel):
    """Esquema para entregar audiencias"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    tiempo: datetime
    tipo_audiencia: str
    expediente: str
    actores: str
    demandados: str
    sala: str
    caracter: str
    causa_penal: str
    delitos: str
    toca: str
    expediente_origen: str
    imputados: str
    origen: str
    model_config = ConfigDict(from_attributes=True)


class OneAudienciaOut(BaseModel):
    """Esquema para entregar una audiencia"""

    success: bool
    message: str
    data: AudienciaOut | None = None
