"""
Estados
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.estados import Estado
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.estados import EstadoOut

estados = APIRouter(prefix="/estados")


@estados.get("", response_model=CustomPage[EstadoOut])
def estados_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Estados paginado"""
    if current_user.permissions.get("ESTADOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Estado).where(Estado.estatus == "A").order_by(Estado.clave)
    return paginate(session, stmt)
