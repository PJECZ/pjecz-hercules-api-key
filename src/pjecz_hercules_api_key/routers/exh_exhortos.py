"""
EXH Exhortos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.exh_exhortos import ExhExhorto
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.exh_exhortos import ExhExhortoOut

exh_exhortos = APIRouter(prefix="/exh_exhortos")


@exh_exhortos.get("", response_model=CustomPage[ExhExhortoOut])
def exh_exhortos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """EXH Exhortos paginado"""
    if current_user.permissions.get("EXH EXHORTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ExhExhorto).where(ExhExhorto.estatus == "A").order_by(ExhExhorto.id.desc())
    return paginate(session, stmt)
