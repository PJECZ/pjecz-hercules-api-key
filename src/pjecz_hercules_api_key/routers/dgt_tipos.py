"""
DGT Tipos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.dgt_tipos import DgtTipo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.dgt_tipos import DgtTipoOut

dgt_tipos = APIRouter(prefix="/dgt_tipos")


@dgt_tipos.get("", response_model=CustomPage[DgtTipoOut])
def dgt_tipos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """DGT Tipos paginado"""
    if current_user.permissions.get("DGT TIPOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(DgtTipo).where(DgtTipo.estatus == "A").order_by(DgtTipo.clave)
    return paginate(session, stmt)
