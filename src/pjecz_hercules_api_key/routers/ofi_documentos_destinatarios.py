"""
Oficios Documentos Destinatarios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.ofi_documentos_destinatarios import OfiDocumentoDestinatario
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.ofi_documentos_destinatarios import OfiDocumentoDestinatarioOut

ofi_documentos_destinatarios = APIRouter(prefix="/ofi_documentos_destinatarios")


@ofi_documentos_destinatarios.get("", response_model=CustomPage[OfiDocumentoDestinatarioOut])
def ofi_documentos_destinatarios_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Oficios Documentos Destinatarios paginado"""
    if current_user.permissions.get("OFI DOCUMENTOS DESTINATARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(OfiDocumentoDestinatario).where(OfiDocumentoDestinatario.estatus == "A").order_by(OfiDocumentoDestinatario.creado.desc())
    return paginate(session, stmt)
