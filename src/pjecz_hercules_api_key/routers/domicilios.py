"""
Domicilios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.domicilios import Domicilio
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.domicilios import DomicilioOut

domicilios = APIRouter(prefix="/domicilios")


@domicilios.get("", response_model=CustomPage[DomicilioOut])
def paginado_domicilios(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    distrito_clave: Annotated[str | None, Query()] = None,
):
    """Domicilios paginados"""
    if current_user.permissions.get("DOMICILIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Domicilio)
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        stmt = stmt.join(Domicilio.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    stmt = stmt.order_by(Domicilio.edificio)
    return paginate(session, stmt)
