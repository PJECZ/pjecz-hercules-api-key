"""
DGT Rutas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave
from pjecz_hercules_api_key.models.dgt_rutas import DgtRuta
from pjecz_hercules_api_key.models.dgt_tipos import DgtTipo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.dgt_rutas import DgtRutaOut

dgt_rutas = APIRouter(prefix="/dgt_rutas")


@dgt_rutas.get("", response_model=CustomPage[DgtRutaOut])
def dgt_rutas_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    clave: Annotated[str | None, Query()] = None,
    autoridad_clave: Annotated[str | None, Query()] = None,
    dgt_tipo_clave: Annotated[str | None, Query()] = None,
):
    """DGT Rutas paginado"""
    if current_user.permissions.get("DGT RUTAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(DgtRuta).where(DgtRuta.estatus == "A")
    if clave and (clave := safe_clave(clave, 64)):
        stmt = stmt.where(DgtRuta.clave.ilike(f"%{clave}%"))
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.where(DgtRuta.autoridad_clave.ilike(f"%{autoridad_clave}%"))
    if dgt_tipo_clave and (dgt_tipo_clave := safe_clave(dgt_tipo_clave, 64)):
        stmt = stmt.join(DgtRuta.dgt_tipo).where(DgtTipo.clave.ilike(f"%{dgt_tipo_clave}%"))
    stmt = stmt.order_by(DgtRuta.clave)
    return paginate(session, stmt)
