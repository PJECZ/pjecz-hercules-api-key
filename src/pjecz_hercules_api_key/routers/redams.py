"""
REDAMs
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_expediente, safe_string, validate_fechas
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.redams import Redam
from pjecz_hercules_api_key.schemas.redams import RedamOut

redams = APIRouter(prefix="/redams")


@redams.get("", response_model=CustomPage[RedamOut])
def redams_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
    distrito_clave: Annotated[str | None, Query()] = None,
    fecha: Annotated[date | None, Query()] = None,
    fecha_desde: Annotated[date | None, Query()] = None,
    fecha_hasta: Annotated[date | None, Query()] = None,
    nombre: Annotated[str | None, Query()] = None,
    expediente: Annotated[str | None, Query()] = None,
):
    """REDAMs paginado"""
    if current_user.permissions.get("REDAMS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    validate_fechas(fecha, fecha_desde, fecha_hasta)
    stmt = select(Redam).where(Redam.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(Redam.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        if not autoridad_clave:
            stmt = stmt.join(Redam.autoridad)
        stmt = stmt.join(Autoridad.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    if fecha is not None:
        stmt = stmt.where(Redam.fecha == fecha)
    if fecha_desde is not None:
        stmt = stmt.where(Redam.fecha >= fecha_desde)
    if fecha_hasta is not None:
        stmt = stmt.where(Redam.fecha <= fecha_hasta)
    if nombre and (nombre := safe_string(nombre)):
        stmt = stmt.where(Redam.nombre.ilike(f"%{nombre}%"))
    if expediente and (expediente := safe_expediente(expediente)):
        stmt = stmt.where(Redam.expediente == expediente)
    stmt = stmt.order_by(Redam.id.desc())
    return paginate(session, stmt)
