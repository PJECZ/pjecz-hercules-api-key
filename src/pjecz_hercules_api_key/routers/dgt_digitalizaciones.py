"""
DGT Digitalizaciones
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_expediente, safe_string
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.dgt_digitalizaciones import DgtDigitalizacion
from pjecz_hercules_api_key.models.dgt_rutas import DgtRuta
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.dgt_digitalizaciones import DgtDigitalizacionOut

dgt_digitalizaciones = APIRouter(prefix="/dgt_digitalizaciones")


@dgt_digitalizaciones.get("", response_model=CustomPage[DgtDigitalizacionOut])
def dgt_digitalizaciones_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
    dgt_ruta_clave: Annotated[str | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
    expediente: Annotated[str | None, Query()] = None,
    expediente_anio: Annotated[int | None, Query(ge=1900, le=2100)] = None,
    expediente_num: Annotated[int | None, Query(ge=1)] = None,
):
    """DGT Digitalizaciones paginado"""
    if current_user.permissions.get("DGT DIGITALIZACIONES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(DgtDigitalizacion).where(DgtDigitalizacion.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(DgtDigitalizacion.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if dgt_ruta_clave and (dgt_ruta_clave := safe_clave(dgt_ruta_clave, 64)):
        stmt = stmt.join(DgtDigitalizacion.dgt_ruta).where(DgtRuta.clave.ilike(f"%{dgt_ruta_clave}%"))
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(DgtDigitalizacion.descripcion.ilike(f"%{descripcion}%"))
    if expediente and (expediente := safe_expediente(expediente)):
        stmt = stmt.where(DgtDigitalizacion.expediente == expediente)
    if expediente_anio is not None:
        stmt = stmt.where(DgtDigitalizacion.expediente_anio == expediente_anio)
    if expediente_num is not None:
        stmt = stmt.where(DgtDigitalizacion.expediente_num == expediente_num)
    stmt = stmt.order_by(DgtDigitalizacion.creado.desc())
    return paginate(session, stmt)
