"""
Permisos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..models.modulos import Modulo
from ..models.permisos import Permiso
from ..models.roles import Rol
from ..schemas.permisos import PermisoOut

permisos = APIRouter(prefix="/api/v5/permisos", tags=["usuarios"])


@permisos.get("", response_model=CustomPage[PermisoOut])
async def paginado_permisos(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    modulo_id: int | None = None,
    rol_id: int | None = None,
):
    """Paginado de permisos"""
    if current_user.permissions.get("PERMISOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Permiso)
    if modulo_id is not None:
        try:
            modulo = database.query(Modulo).filter(Modulo.id == modulo_id).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe ese módulo")
        if modulo.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese módulo")
        consulta = consulta.join(Modulo).filter(Modulo.id == modulo_id)
    if rol_id is not None:
        try:
            rol = database.query(Rol).filter(Rol.id == rol_id).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe ese rol")
        if rol.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese rol")
        consulta = consulta.join(Rol).filter(Rol.id == rol_id)
    return paginate(consulta.filter(Permiso.estatus == "A").order_by(Permiso.id.desc()))
