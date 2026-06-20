"""
Modulos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.schemas.modulos import ModuloOut

from pjecz_hercules_api_key.models.modulos import Modulo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas
modulos = APIRouter(prefix="/api/v5/modulos", tags=["usuarios"])


@modulos.get("", response_model=CustomPage[ModuloOut])
async def paginado_modulos(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de módulos"""
    if current_user.permissions.get("MODULOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return paginate(database.query(Modulo).filter_by(estatus="A").order_by(Modulo.nombre))
