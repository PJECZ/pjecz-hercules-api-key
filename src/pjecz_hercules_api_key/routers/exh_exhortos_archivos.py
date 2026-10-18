"""
EXH Exhortos Archivos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.exh_exhortos_archivos import ExhExhortoArchivo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.exh_exhortos_archivos import ExhExhortoArchivoOut

exh_exhortos_archivos = APIRouter(prefix="/exh_exhortos_archivos")


@exh_exhortos_archivos.get("", response_model=CustomPage[ExhExhortoArchivoOut])
def exh_exhortos_archivos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """EXH Exhortos Archivos paginado"""
    if current_user.permissions.get("EXH EXHORTOS ARCHIVOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ExhExhortoArchivo).where(ExhExhortoArchivo.estatus == "A").order_by(ExhExhortoArchivo.id.desc())
    return paginate(session, stmt)
