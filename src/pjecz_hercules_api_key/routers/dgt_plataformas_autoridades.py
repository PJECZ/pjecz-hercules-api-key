"""
DGT Plataformas Autoridades
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.dgt_plataformas_autoridades import DgtPlataformaAutoridad
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.dgt_plataformas_autoridades import DgtPlataformaAutoridadOut

dgt_plataformas_autoridades = APIRouter(prefix="/dgt_plataformas_autoridades")


@dgt_plataformas_autoridades.get("", response_model=CustomPage[DgtPlataformaAutoridadOut])
def dgt_plataformas_autoridades_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """DGT Plataformas Autoridades paginado"""
    if current_user.permissions.get("DGT PLATAFORMAS AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = (
        select(DgtPlataformaAutoridad)
        .where(DgtPlataformaAutoridad.estatus == "A")
        .order_by(DgtPlataformaAutoridad.creado.desc())
    )
    return paginate(session, stmt)
