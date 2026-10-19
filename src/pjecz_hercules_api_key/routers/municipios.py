"""
Municipios
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
from pjecz_hercules_api_key.models.municipios import Municipio
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.municipios import MunicipioOut

municipios = APIRouter(prefix="/municipios")


@municipios.get("", response_model=CustomPage[MunicipioOut])
def municipios_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    clave: Annotated[str | None, Query()] = None,
    nombre: Annotated[str | None, Query()] = None,
    estado_clave: Annotated[str | None, Query()] = None,
):
    """Municipios paginado"""
    if current_user.permissions.get("MUNICIPIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Municipio).where(Municipio.estatus == "A")
    if clave and (clave := safe_clave(clave)):
        stmt = stmt.where(Municipio.clave.ilike(f"%{clave}%"))
    if nombre and (nombre := safe_string(nombre)):
        stmt = stmt.where(Municipio.nombre.ilike(f"%{nombre}%"))
    if estado_clave and (estado_clave := safe_clave(estado_clave)):
        stmt = stmt.join(Municipio.estado).where(Estado.clave.ilike(f"%{estado_clave}%"))
    stmt = stmt.order_by(Municipio.estado_id, Municipio.clave)
    return paginate(session, stmt)
