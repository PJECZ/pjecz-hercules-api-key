"""
Sentencias
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
from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.sentencias import Sentencia
from pjecz_hercules_api_key.schemas.sentencias import SentenciaOut

sentencias = APIRouter(prefix="/sentencias")


@sentencias.get("", response_model=CustomPage[SentenciaOut])
def sentencias_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
    distrito_clave: Annotated[str | None, Query()] = None,
    materia_clave: Annotated[str | None, Query()] = None,
    fecha: Annotated[date | None, Query()] = None,
    fecha_desde: Annotated[date | None, Query()] = None,
    fecha_hasta: Annotated[date | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
    expediente: Annotated[str | None, Query()] = None,
    expediente_anio: Annotated[int | None, Query(ge=1900, le=2100)] = None,
    expediente_num: Annotated[int | None, Query(ge=1)] = None,
):
    """Sentencias paginado"""
    if current_user.permissions.get("SENTENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    validate_fechas(fecha, fecha_desde, fecha_hasta)
    stmt = select(Sentencia).where(Sentencia.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(Sentencia.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        if not autoridad_clave:
            stmt = stmt.join(Sentencia.autoridad)
        stmt = stmt.join(Autoridad.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    if materia_clave and (materia_clave := safe_clave(materia_clave)):
        stmt = (
            stmt.join(Sentencia.materia_tipo_juicio)
            .join(MateriaTipoJuicio.materia)
            .where(Materia.clave.ilike(f"%{materia_clave}%"))
        )
    if fecha is not None:
        stmt = stmt.where(Sentencia.fecha == fecha)
    if fecha_desde is not None:
        stmt = stmt.where(Sentencia.fecha >= fecha_desde)
    if fecha_hasta is not None:
        stmt = stmt.where(Sentencia.fecha <= fecha_hasta)
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(Sentencia.descripcion.ilike(f"%{descripcion}%"))
    if expediente and (expediente := safe_expediente(expediente)):
        stmt = stmt.where(Sentencia.expediente == expediente)
    if expediente_anio is not None:
        stmt = stmt.where(Sentencia.expediente_anio == expediente_anio)
    if expediente_num is not None:
        stmt = stmt.where(Sentencia.expediente_num == expediente_num)
    stmt = stmt.order_by(Sentencia.id.desc())
    return paginate(session, stmt)
