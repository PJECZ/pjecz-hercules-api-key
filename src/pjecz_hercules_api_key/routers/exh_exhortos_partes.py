"""
EXH Exhortos Partes
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.exh_exhortos_partes import ExhExhortoParte
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.exh_exhortos_partes import ExhExhortoParteOut

exh_exhortos_partes = APIRouter(prefix="/exh_exhortos_partes")


@exh_exhortos_partes.get("", response_model=CustomPage[ExhExhortoParteOut])
def exh_exhortos_partes_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """EXH Exhortos Partes paginado"""
    if current_user.permissions.get("EXH EXHORTOS PARTES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ExhExhortoParte).where(ExhExhortoParte.estatus == "A").order_by(ExhExhortoParte.id.desc())
    return paginate(session, stmt)
