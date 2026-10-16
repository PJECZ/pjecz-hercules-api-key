"""
Edictos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.models.edictos import Edicto
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.edictos import EdictoOut

edictos = APIRouter(prefix="/api/edictos")


@edictos.get("", response_model=LimitOffsetPage[EdictoOut])
def edictos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Edictos paginado"""
    if current_user.permissions.get("EDICTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Edicto).where(Edicto.estatus == "A").order_by(Edicto.id.desc())
    return paginate(session, stmt)
