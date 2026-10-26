"""
Archivos Juzgados Extintos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_string
from pjecz_hercules_api_key.models.arc_juzgados_extintos import ArcJuzgadoExtinto
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.arc_juzgados_extintos import ArcJuzgadoExtintoOut

arc_juzgados_extintos = APIRouter(prefix="/arc_juzgados_extintos")


@arc_juzgados_extintos.get("", response_model=CustomPage[ArcJuzgadoExtintoOut])
def arc_juzgados_extintos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    clave: Annotated[str | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
    distrito_clave: Annotated[str | None, Query()] = None,
):
    """Archivos Juzgados Extintos paginado"""
    if current_user.permissions.get("ARC JUZGADOS EXTINTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ArcJuzgadoExtinto).where(ArcJuzgadoExtinto.estatus == "A")
    if clave and (clave := safe_clave(clave)):
        stmt = stmt.where(ArcJuzgadoExtinto.clave.ilike(f"%{clave}%"))
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(ArcJuzgadoExtinto.descripcion.ilike(f"%{descripcion}%"))
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        stmt = stmt.join(ArcJuzgadoExtinto.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    stmt = stmt.order_by(ArcJuzgadoExtinto.clave)
    return paginate(session, stmt)
