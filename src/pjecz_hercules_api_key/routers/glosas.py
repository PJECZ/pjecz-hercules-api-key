"""
Glosas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.models.glosas import Glosa
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.glosas import GlosaOut

glosas = APIRouter(prefix="/api/glosas")


@glosas.get("", response_model=LimitOffsetPage[GlosaOut])
def glosas_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Glosas paginado"""
    if current_user.permissions.get("GLOSAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Glosa).where(Glosa.estatus == "A").order_by(Glosa.id.desc())
    return paginate(session, stmt)
