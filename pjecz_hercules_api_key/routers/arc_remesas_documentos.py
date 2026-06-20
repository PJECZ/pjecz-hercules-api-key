"""
Arc Remesas Documentos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.schemas.arc_remesas_documentos import ArcRemesaDocumentoOut

from pjecz_hercules_api_key.models.arc_remesas_documentos import ArcRemesaDocumento
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas
arc_remesas_documentos = APIRouter(prefix="/api/v5/arc_remesas_documentos", tags=["archivos"])


@arc_remesas_documentos.get("", response_model=CustomPage[ArcRemesaDocumentoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de documentos de remesas"""
    if current_user.permissions.get("ARC REMESAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(ArcRemesaDocumento)
    return paginate(consulta.filter(ArcRemesaDocumento.estatus == "A").order_by(ArcRemesaDocumento.id.desc()))
