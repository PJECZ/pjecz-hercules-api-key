"""
Oficios Documentos Destinatarios, esquemas
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OfiDocumentoDestinatarioOut(BaseModel):
    """Esquema para entregar destinatarios"""

    id: uuid.UUID
    ofi_documento_id: uuid.UUID
    usuario_email: str
    usuario_nombre: str
    usuario_autoridad_clave: str
    con_copia: bool
    fue_leido: bool
    fue_leido_tiempo: datetime | None
    model_config = ConfigDict(from_attributes=True)


class OneOfiDocumentoDestinatarioOut(BaseModel):
    """Esquema para entregar un destinatario"""

    success: bool
    message: str
    data: OfiDocumentoDestinatarioOut | None = None
