"""
DGT Depósitos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_string
from pjecz_hercules_api_key.models.dgt_depositos import DgtDepositos
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.dgt_depositos import DgtDepositoOut

dgt_depositos = APIRouter(prefix="/dgt_depositos")


@dgt_depositos.get("", response_model=CustomPage[DgtDepositoOut])
def dgt_depositos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    clave: Annotated[str | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
):
    """DGT Depósitos paginado"""
    if current_user.permissions.get("DGT DEPOSITOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(DgtDepositos).where(DgtDepositos.estatus == "A")
    if clave and (clave := safe_clave(clave, 64)):
        stmt = stmt.where(DgtDepositos.clave.ilike(f"%{clave}%"))
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(DgtDepositos.descripcion.ilike(f"%{descripcion}%"))
    stmt = stmt.order_by(DgtDepositos.clave)
    return paginate(session, stmt)
