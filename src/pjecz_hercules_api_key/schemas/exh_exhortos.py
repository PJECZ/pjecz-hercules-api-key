"""
EXH Exhortos
"""

from pydantic import BaseModel, ConfigDict


class ExhExhortoOut(BaseModel):
    """Esquema para entregar exhortos"""

    id: int
    autoridad_clave: str
    exh_area_clave: str
    municipio_origen_clave: str
    municipio_origen_nombre: str
    exhorto_origen_id: str
    municipio_destino_clave: str
    municipio_destino_nombre: str
    materia_clave: str
    materia_nombre: str
    juzgado_origen_id: str | None = None
    juzgado_origen_nombre: str
    numero_expediente_origen: str
    tipo_juicio_asunto_delitos: str
    remitente: str
    estado: str
    model_config = ConfigDict(from_attributes=True)


class OneExhExhortoOut(BaseModel):
    """Esquema para entrega un exhorto"""

    success: bool
    message: str
    data: ExhExhortoOut | None = None
