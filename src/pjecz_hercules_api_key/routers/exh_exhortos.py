"""
EXH Exhortos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.exh_areas import ExhArea
from pjecz_hercules_api_key.models.exh_exhortos import ExhExhorto
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.exh_exhortos import ExhExhortoOut

exh_exhortos = APIRouter(prefix="/exh_exhortos")


@exh_exhortos.get("", response_model=CustomPage[ExhExhortoOut])
def exh_exhortos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
    exh_area_clave: Annotated[str | None, Query()] = None,
    materia_clave: Annotated[str | None, Query()] = None,
):
    """EXH Exhortos paginado"""
    if current_user.permissions.get("EXH EXHORTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ExhExhorto).where(ExhExhorto.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(ExhExhorto.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if exh_area_clave and (exh_area_clave := safe_clave(exh_area_clave)):
        stmt = stmt.join(ExhExhorto.exh_area).where(ExhArea.clave.ilike(f"%{exh_area_clave}%"))
    if materia_clave and (materia_clave := safe_clave(materia_clave, 32)):
        stmt = stmt.where(ExhExhorto.materia_clave.ilike(f"%{materia_clave}%"))
    stmt = stmt.order_by(ExhExhorto.id.desc())
    return paginate(session, stmt)
