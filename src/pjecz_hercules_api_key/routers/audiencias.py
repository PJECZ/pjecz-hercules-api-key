"""
Audiencias
"""

from datetime import date, datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_expediente, validate_fechas
from pjecz_hercules_api_key.models.audiencias import Audiencia
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.audiencias import AudienciaOut, OneAudienciaOut

audiencias = APIRouter(prefix="/audiencias")


@audiencias.get("", response_model=CustomPage[AudienciaOut])
def audiencias_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
    distrito_clave: Annotated[str | None, Query()] = None,
    expediente: Annotated[str | None, Query()] = None,
    fecha: Annotated[date | None, Query()] = None,
    fecha_desde: Annotated[date | None, Query()] = None,
    fecha_hasta: Annotated[date | None, Query()] = None,
):
    """Audiencias paginado"""
    if current_user.permissions.get("AUDIENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    validate_fechas(fecha, fecha_desde, fecha_hasta)
    stmt = select(Audiencia).where(Audiencia.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(Audiencia.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        if not autoridad_clave:
            stmt = stmt.join(Audiencia.autoridad)
        stmt = stmt.join(Autoridad.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    if expediente and (expediente := safe_expediente(expediente)):
        stmt = stmt.where(Audiencia.expediente == expediente)
    if fecha is not None:
        fecha_desde = fecha_hasta = fecha
    if fecha_desde is not None:
        stmt = stmt.where(Audiencia.tiempo >= datetime.combine(fecha_desde, time.min))
    if fecha_hasta is not None:
        stmt = stmt.where(Audiencia.tiempo <= datetime.combine(fecha_hasta, time(23, 59, 59)))
    stmt = stmt.order_by(Audiencia.tiempo.asc())
    return paginate(session, stmt)


@audiencias.get("/{id}", response_model=OneAudienciaOut)
def audiencias_detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    id: int,
):
    """Detalle de una Audiencia"""
    if current_user.permissions.get("AUDIENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    audiencia = session.get(Audiencia, id)
    if audiencia is None or audiencia.estatus != "A":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return OneAudienciaOut(success=True, message="Success", data=AudienciaOut.model_validate(audiencia))
