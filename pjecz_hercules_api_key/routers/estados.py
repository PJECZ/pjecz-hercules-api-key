"""
Estados
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..models.estados import Estado
from ..models.permisos import Permiso
from ..schemas.estados import EstadoOut

estados = APIRouter(prefix="/api/v5/estados", tags=["municipios"])


@estados.get("", response_model=CustomPage[EstadoOut])
async def paginado_estados(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de estados"""
    if current_user.permissions.get("ESTADOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return paginate(database.query(Estado).filter(Estado.estatus == "A").order_by(Estado.edificio))
