"""
Permisos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.permisos import PermisoOut

permisos = APIRouter(prefix="/permisos")


@permisos.get("", response_model=CustomPage[PermisoOut])
def permisos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Permisos paginado"""
    if current_user.permissions.get("PERMISOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Permiso).where(Permiso.estatus == "A").order_by(Permiso.nombre)
    return paginate(session, stmt)
