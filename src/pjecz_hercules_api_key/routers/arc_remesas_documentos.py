"""
Archivos Remesas Documentos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.arc_remesas_documentos import ArcRemesaDocumento
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.arc_remesas_documentos import ArcRemesaDocumentoOut

arc_remesas_documentos = APIRouter(prefix="/arc_remesas_documentos")


@arc_remesas_documentos.get("", response_model=CustomPage[ArcRemesaDocumentoOut])
def arc_remesas_documentos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Archivos Remesas Documentos paginado"""
    if current_user.permissions.get("ARC REMESAS", 0) < Permiso.VER:  # TODO: Crear un Modulo con el nombre especifico
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ArcRemesaDocumento).where(ArcRemesaDocumento.estatus == "A").order_by(ArcRemesaDocumento.id.desc())
    return paginate(session, stmt)
