"""
Archivos Remesas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave
from pjecz_hercules_api_key.models.arc_remesas import ArcRemesa
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.arc_remesas import ArcRemesaOut

arc_remesas = APIRouter(prefix="/arc_remesas")


@arc_remesas.get("", response_model=CustomPage[ArcRemesaOut])
def arc_remesas_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
):
    """Archivos Remesas paginado"""
    if current_user.permissions.get("ARC REMESAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ArcRemesa).where(ArcRemesa.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(ArcRemesa.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    stmt = stmt.order_by(ArcRemesa.id.desc())
    return paginate(session, stmt)
