"""
EXH Áreas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_string
from pjecz_hercules_api_key.models.exh_areas import ExhArea
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.exh_areas import ExhAreaOut

exh_areas = APIRouter(prefix="/exh_areas")


@exh_areas.get("", response_model=CustomPage[ExhAreaOut])
def exh_areas_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    clave: Annotated[str | None, Query()] = None,
    nombre: Annotated[str | None, Query()] = None,
):
    """EXH Áreas paginado"""
    if current_user.permissions.get("EXH AREAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ExhArea).where(ExhArea.estatus == "A")
    if clave and (clave := safe_clave(clave)):
        stmt = stmt.where(ExhArea.clave.ilike(f"%{clave}%"))
    if nombre and (nombre := safe_string(nombre)):
        stmt = stmt.where(ExhArea.nombre.ilike(f"%{nombre}%"))
    stmt = stmt.order_by(ExhArea.clave)
    return paginate(session, stmt)
