"""
DGT Plataformas Endpoints
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.dgt_plataformas_endpoints import DgtPlataformaEndpoint
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.dgt_plataformas_endpoints import DgtPlataformaEndpointOut

dgt_plataformas_endpoints = APIRouter(prefix="/dgt_plataformas_endpoints")


@dgt_plataformas_endpoints.get("", response_model=CustomPage[DgtPlataformaEndpointOut])
def dgt_plataformas_endpoints_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """DGT Plataformas Endpoints paginado"""
    if current_user.permissions.get("DGT PLATAFORMAS ENDPOINTS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(DgtPlataformaEndpoint).where(DgtPlataformaEndpoint.estatus == "A").order_by(DgtPlataformaEndpoint.descripcion)
    return paginate(session, stmt)
