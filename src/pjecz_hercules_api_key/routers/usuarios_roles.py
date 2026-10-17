"""
Usuarios-Roles
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.usuarios_roles import UsuarioRol
from pjecz_hercules_api_key.schemas.usuarios_roles import UsuarioRolOut

usuarios_roles = APIRouter(prefix="/api/usuarios_roles")


@usuarios_roles.get("", response_model=CustomPage[UsuarioRolOut])
def usuarios_roles_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Usuarios-Roles paginado"""
    if current_user.permissions.get("USUARIOS ROLES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(UsuarioRol).where(UsuarioRol.estatus == "A").order_by(UsuarioRol.id)
    return paginate(session, stmt)
