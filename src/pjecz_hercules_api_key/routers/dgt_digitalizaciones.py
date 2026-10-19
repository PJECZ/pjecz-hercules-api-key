"""
DGT Digitalizaciones
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.dgt_digitalizaciones import DgtDigitalizacion
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.dgt_digitalizaciones import DgtDigitalizacionOut

dgt_digitalizaciones = APIRouter(prefix="/dgt_digitalizaciones")


@dgt_digitalizaciones.get("", response_model=CustomPage[DgtDigitalizacionOut])
def dgt_digitalizaciones_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """DGT Digitalizaciones paginado"""
    if current_user.permissions.get("DGT DIGITALIZACIONES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(DgtDigitalizacion).where(DgtDigitalizacion.estatus == "A").order_by(DgtDigitalizacion.creado.desc())
    return paginate(session, stmt)
