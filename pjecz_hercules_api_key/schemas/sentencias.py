"""
Sentencias, esquemas
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SentenciaOut(BaseModel):
    """Esquema para entregar sentencias"""

    id: int
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    materia_clave: str
    materia_nombre: str
    materia_tipo_juicio_id: int
    materia_tipo_juicio_descripcion: str
    sentencia: str
    sentencia_fecha: date | None = None
    expediente: str
    expediente_anio: int
    expediente_num: int
    fecha: date
    descripcion: str
    es_perspectiva_genero: bool
    model_config = ConfigDict(from_attributes=True)


class OneSentenciaOut(BaseModel):
    """Esquema para entregar una sentencia"""

    success: bool
    message: str
    data: SentenciaOut | None = None
