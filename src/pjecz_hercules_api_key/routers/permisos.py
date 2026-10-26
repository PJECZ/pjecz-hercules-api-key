"""
Permisos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_string
from pjecz_hercules_api_key.models.modulos import Modulo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.roles import Rol
from pjecz_hercules_api_key.schemas.permisos import PermisoOut

permisos = APIRouter(prefix="/permisos")


@permisos.get("", response_model=CustomPage[PermisoOut])
def permisos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    modulo_nombre: Annotated[str | None, Query()] = None,
    rol_nombre: Annotated[str | None, Query()] = None,
):
    """Permisos paginado"""
    if current_user.permissions.get("PERMISOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Permiso).where(Permiso.estatus == "A")
    if modulo_nombre and (modulo_nombre := safe_string(modulo_nombre)):
        stmt = stmt.join(Permiso.modulo).where(Modulo.nombre.ilike(f"%{modulo_nombre}%"))
    if rol_nombre and (rol_nombre := safe_string(rol_nombre)):
        stmt = stmt.join(Permiso.rol).where(Rol.nombre.ilike(f"%{rol_nombre}%"))
    stmt = stmt.order_by(Permiso.nombre)
    return paginate(session, stmt)
