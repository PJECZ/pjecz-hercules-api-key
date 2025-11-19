"""
Usuarios-Roles
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_email
from ..models.permisos import Permiso
from ..models.roles import Rol
from ..models.usuarios import Usuario
from ..models.usuarios_roles import UsuarioRol
from ..schemas.usuarios_roles import UsuarioRolOut

usuarios_roles = APIRouter(prefix="/api/v5/usuarios_roles", tags=["usuarios"])


@usuarios_roles.get("", response_model=CustomPage[UsuarioRolOut])
async def paginado_usuarios_roles(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    rol_id: int | None = None,
    usuario_email: str | None = None,
):
    """Paginado de usuarios-roles"""
    if current_user.permissions.get("USUARIOS ROLES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(UsuarioRol)
    if rol_id is not None:
        try:
            rol = database.query(Rol).filter(Rol.id == rol_id).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe ese rol")
        if rol.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese rol")
        consulta = consulta.join(Rol).filter(Rol.id == rol_id)
    if usuario_email is not None:
        try:
            usuario_email = safe_email(usuario_email)
        except ValueError:
            return CustomPage(success=False, message="No es válido el email")
        try:
            usuario = database.query(Usuario).filter(Usuario.email == usuario_email).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe ese usuario")
        if usuario.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese usuario")
        consulta = consulta.join(Usuario).filter(Usuario.email == usuario_email)
    return paginate(consulta.filter(UsuarioRol.estatus == "A").order_by(UsuarioRol.id.desc()))
