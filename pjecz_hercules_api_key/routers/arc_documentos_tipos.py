"""
Arc Documentos Tipos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.models.arc_documentos_tipos import ArcDocumentoTipo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.arc_documentos_tipos import ArcDocumentoTipoOut

arc_documentos_tipos = APIRouter(prefix="/api/v5/arc_documentos_tipos", tags=["archivos"])


@arc_documentos_tipos.get("", response_model=CustomPage[ArcDocumentoTipoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de tipos de documentos"""
    if current_user.permissions.get("ARC DOCUMENTOS TIPOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(ArcDocumentoTipo)
    return paginate(consulta.filter(ArcDocumentoTipo.estatus == "A").order_by(ArcDocumentoTipo.nombre))
