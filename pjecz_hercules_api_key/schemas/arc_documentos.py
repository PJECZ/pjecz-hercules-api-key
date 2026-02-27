"""
Arc Documentos, esquemas
"""

from pydantic import BaseModel, ConfigDict


class ArcDocumentoOut(BaseModel):
    """Esquema para entregar documentos"""

    id: int
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    arc_documento_tipo_id: int
    arc_documento_tipo_nombre: str
    actor: str
    demandado: str | None
    expediente: str
    anio: int
    expediente_numero: int | None
    juicio: str | None
    arc_juzgados_origen_claves: str | None
    fojas: int
    tipo_juzgado: str
    ubicacion: str
    model_config = ConfigDict(from_attributes=True)


class OneArcDocumentoOut(BaseModel):
    """Esquema para entregar un documento"""

    success: bool
    message: str
    data: ArcDocumentoOut | None = None
