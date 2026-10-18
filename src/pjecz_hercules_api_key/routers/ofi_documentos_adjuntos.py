"""
Oficios Documentos Adjuntos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.ofi_documentos_adjuntos import OfiDocumentoAdjunto
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.ofi_documentos_adjuntos import OfiDocumentoAdjuntoOut

ofi_documentos_adjuntos = APIRouter(prefix="/ofi_documentos_adjuntos")


@ofi_documentos_adjuntos.get("", response_model=CustomPage[OfiDocumentoAdjuntoOut])
def ofi_documentos_adjuntos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Oficios Documentos Adjuntos paginado"""
    if current_user.permissions.get("OFI DOCUMENTOS ADJUNTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(OfiDocumentoAdjunto).where(OfiDocumentoAdjunto.estatus == "A").order_by(OfiDocumentoAdjunto.creado.desc())
    return paginate(session, stmt)
