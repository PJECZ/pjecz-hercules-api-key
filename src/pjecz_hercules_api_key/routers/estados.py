"""
Estados
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_string
from pjecz_hercules_api_key.models.estados import Estado
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.estados import EstadoOut

estados = APIRouter(prefix="/estados")


@estados.get("", response_model=CustomPage[EstadoOut])
def estados_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    clave: Annotated[str | None, Query()] = None,
    nombre: Annotated[str | None, Query()] = None,
):
    """Estados paginado"""
    if current_user.permissions.get("ESTADOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Estado).where(Estado.estatus == "A")
    if clave and (clave := safe_clave(clave)):
        stmt = stmt.where(Estado.clave.ilike(f"%{clave}%"))
    if nombre and (nombre := safe_string(nombre)):
        stmt = stmt.where(Estado.nombre.ilike(f"%{nombre}%"))
    stmt = stmt.order_by(Estado.clave)
    return paginate(session, stmt)
