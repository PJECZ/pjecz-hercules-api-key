"""
DGT Plataformas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.dgt_plataformas import DgtPlataforma
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.dgt_plataformas import DgtPlataformaOut

dgt_plataformas = APIRouter(prefix="/dgt_plataformas")


@dgt_plataformas.get("", response_model=CustomPage[DgtPlataformaOut])
def dgt_plataformas_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """DGT Plataformas paginado"""
    if current_user.permissions.get("DGT PLATAFORMAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(DgtPlataforma).where(DgtPlataforma.estatus == "A").order_by(DgtPlataforma.descripcion)
    return paginate(session, stmt)
