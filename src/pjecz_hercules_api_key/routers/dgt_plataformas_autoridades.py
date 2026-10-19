"""
DGT Plataformas Autoridades
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.dgt_plataformas import DgtPlataforma
from pjecz_hercules_api_key.models.dgt_plataformas_autoridades import DgtPlataformaAutoridad
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.dgt_plataformas_autoridades import DgtPlataformaAutoridadOut

dgt_plataformas_autoridades = APIRouter(prefix="/dgt_plataformas_autoridades")


@dgt_plataformas_autoridades.get("", response_model=CustomPage[DgtPlataformaAutoridadOut])
def dgt_plataformas_autoridades_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
    dgt_plataforma_clave: Annotated[str | None, Query()] = None,
):
    """DGT Plataformas Autoridades paginado"""
    if current_user.permissions.get("DGT PLATAFORMAS AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(DgtPlataformaAutoridad).where(DgtPlataformaAutoridad.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(DgtPlataformaAutoridad.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if dgt_plataforma_clave and (dgt_plataforma_clave := safe_clave(dgt_plataforma_clave, 64)):
        stmt = stmt.join(DgtPlataformaAutoridad.dgt_plataforma).where(DgtPlataforma.clave.ilike(f"%{dgt_plataforma_clave}%"))
    stmt = stmt.order_by(DgtPlataformaAutoridad.creado.desc())
    return paginate(session, stmt)
