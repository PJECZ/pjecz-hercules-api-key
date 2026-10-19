"""
Oficinas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_string
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.domicilios import Domicilio
from pjecz_hercules_api_key.models.oficinas import Oficina
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.oficinas import OficinaOut

oficinas = APIRouter(prefix="/oficinas")


@oficinas.get("", response_model=CustomPage[OficinaOut])
def paginado_oficinas(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    clave: Annotated[str | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
    distrito_clave: Annotated[str | None, Query()] = None,
    domicilio_edificio: Annotated[str | None, Query()] = None,
):
    """Oficinas paginadas"""
    if current_user.permissions.get("OFICINAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Oficina)
    if clave and (clave := safe_clave(clave, 32)):
        stmt = stmt.where(Oficina.clave.ilike(f"%{clave}%"))
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(Oficina.descripcion.ilike(f"%{descripcion}%"))
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        stmt = stmt.join(Oficina.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    if domicilio_edificio and (domicilio_edificio := safe_string(domicilio_edificio)):
        stmt = stmt.join(Oficina.domicilio).where(Domicilio.edificio.ilike(f"%{domicilio_edificio}%"))
    stmt = stmt.order_by(Oficina.clave)
    return paginate(session, stmt)
