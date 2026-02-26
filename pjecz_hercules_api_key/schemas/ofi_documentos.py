"""
Oficios Documentos, esquemas
"""

import uuid

from pydantic import BaseModel, ConfigDict


class OfiDocumentoOut(BaseModel):
    """Esquema para entregar documentos"""

    id: uuid.UUID
    usuario_email: str
    usuario_nombre: str
    usuario_autoridad_clave: str
    descripcion: str
    estado: str
    esta_archivado: bool
    esta_cancelado: bool
    folio: str | None
    folio_anio: int | None
    folio_num: int | None
    contenido_html: str | None
    contenido_md: str | None
    firma_simple: str
    model_config = ConfigDict(from_attributes=True)


class OneOfiDocumentoOut(BaseModel):
    """Esquema para entregar un documento"""

    success: bool
    message: str
    data: OfiDocumentoOut | None = None
