"""
Exh Exhortos, esquemas
"""

from pydantic import BaseModel, ConfigDict

from pjecz_hercules_api_key.schemas.exh_exhortos_archivos import ExhExhortoArchivoIn, ExhExhortoArchivoOut
from pjecz_hercules_api_key.schemas.exh_exhortos_partes import ExhExhortoParteIn, ExhExhortoParteOut


class ExhExhortoOut(BaseModel):
    """Esquema para entregar exhortos"""

    id: int
    autoridad_clave: str
    exh_area_clave: str
    # municipio_origen_id: int
    municipio_origen_clave: str
    municipio_origen_nombre: str
    exhorto_origen_id: str
    # municipio_destino_id: int
    municipio_destino_clave: str
    municipio_destino_nombre: str
    materia_clave: str
    materia_nombre: str
    juzgado_origen_id: str
    juzgado_origen_nombre: str
    numero_expediente_origen: str
    tipo_juicio_asunto_delitos: str
    fojas: int
    dias_responder: int
    remitente: str
    estado: str
    exh_exhorto_partes: list[ExhExhortoParteOut]
    exh_exhorto_archivos: list[ExhExhortoArchivoOut]
    model_config = ConfigDict(from_attributes=True)


class ExhExhortoPaginadoOut(BaseModel):
    """Esquema para entregar exhortos paginados"""

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
    juzgado_origen_id: str
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


class ExhExhortoIn(BaseModel):
    """Esquema para recibir exhortos"""

    autoridad_clave: str
    exh_area_clave: str
    # municipio_origen_id: int
    exhorto_origen_id: str
    # municipio_destino_id: int
    materia_clave: str
    juzgado_origen_id: str
    juzgado_origen_nombre: str
    numero_expediente_origen: str
    tipo_juicio_asunto_delitos: str
    fojas: int
    dias_responder: int
    exh_exhorto_partes: list[ExhExhortoParteIn]
    exh_exhorto_archivos: list[ExhExhortoArchivoIn]
