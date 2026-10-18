"""
Oficios Documentos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.ofi_documentos import OfiDocumento
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.ofi_documentos import OfiDocumentoOut

ofi_documentos = APIRouter(prefix="/ofi_documentos")


@ofi_documentos.get("", response_model=CustomPage[OfiDocumentoOut])
def ofi_documentos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Oficios Documentos paginado"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(OfiDocumento).where(OfiDocumento.estatus == "A").order_by(OfiDocumento.creado.desc())
    return paginate(session, stmt)
