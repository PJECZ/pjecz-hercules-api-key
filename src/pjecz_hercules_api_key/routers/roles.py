"""
Roles
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_string
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.roles import Rol
from pjecz_hercules_api_key.schemas.roles import RolOut

roles = APIRouter(prefix="/roles")


@roles.get("", response_model=CustomPage[RolOut])
def roles_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    nombre: Annotated[str | None, Query()] = None,
):
    """Roles paginado"""
    if current_user.permissions.get("ROLES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Rol).where(Rol.estatus == "A")
    if nombre and (nombre := safe_string(nombre)):
        stmt = stmt.where(Rol.nombre.ilike(f"%{nombre}%"))
    stmt = stmt.order_by(Rol.nombre)
    return paginate(session, stmt)
