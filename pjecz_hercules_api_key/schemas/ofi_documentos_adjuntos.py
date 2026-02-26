"""
Oficios Documentos Adjuntos, esquemas
"""

import uuid

from pydantic import BaseModel, ConfigDict


class OfiDocumentoAdjuntoOut(BaseModel):
    """Esquema para entregar adjuntos"""

    id: uuid.UUID
    ofi_documento_id: uuid.UUID
    descripcion: str
    archivo: str
    model_config = ConfigDict(from_attributes=True)


class OneOfiDocumentoAdjuntoOut(BaseModel):
    """Esquema para entregar un adjunto"""

    success: bool
    message: str
    data: OfiDocumentoAdjuntoOut | None = None
