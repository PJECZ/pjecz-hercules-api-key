"""
Archivos Documentos Tipos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.arc_documentos_tipos import ArcDocumentoTipo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.arc_documentos_tipos import ArcDocumentoTipoOut

arc_documentos_tipos = APIRouter(prefix="/arc_documentos_tipos")


@arc_documentos_tipos.get("", response_model=CustomPage[ArcDocumentoTipoOut])
def arc_documentos_tipos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Archivos Documentos Tipos paginado"""
    if current_user.permissions.get("ARC DOCUMENTOS TIPOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ArcDocumentoTipo).where(ArcDocumentoTipo.estatus == "A").order_by(ArcDocumentoTipo.nombre)
    return paginate(session, stmt)
