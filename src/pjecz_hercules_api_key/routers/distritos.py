"""
Distritos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.distritos import DistritoOut

distritos = APIRouter(prefix="/api/distritos")


@distritos.get("", response_model=CustomPage[DistritoOut])
def distritos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Distritos paginado"""
    if current_user.permissions.get("DISTRITOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Distrito).where(Distrito.estatus == "A").order_by(Distrito.clave)
    return paginate(session, stmt)
