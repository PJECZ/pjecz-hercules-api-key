"""
Arc Documentos Tipos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..models.arc_documentos_tipos import ArcDocumentoTipo
from ..models.permisos import Permiso
from ..schemas.arc_documentos_tipos import ArcDocumentoTipoOut

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
