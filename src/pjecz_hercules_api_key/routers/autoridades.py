"""
Autoridades
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_string
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.autoridades import AutoridadOut

autoridades = APIRouter(prefix="/autoridades")


@autoridades.get("", response_model=CustomPage[AutoridadOut])
def autoridades_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    clave: Annotated[str | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
    distrito_clave: Annotated[str | None, Query()] = None,
    materia_clave: Annotated[str | None, Query()] = None,
    es_jurisdiccional: Annotated[bool | None, Query()] = None,
    es_notaria: Annotated[bool | None, Query()] = None,
    es_extinto: Annotated[bool | None, Query()] = None,
):
    """Autoridades paginado"""
    if current_user.permissions.get("AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Autoridad).where(Autoridad.estatus == "A")
    if clave and (clave := safe_clave(clave)):
        stmt = stmt.where(Autoridad.clave.ilike(f"%{clave}%"))
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(Autoridad.descripcion.ilike(f"%{descripcion}%"))
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        stmt = stmt.join(Autoridad.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    if materia_clave and (materia_clave := safe_clave(materia_clave)):
        stmt = stmt.join(Autoridad.materia).where(Materia.clave.ilike(f"%{materia_clave}%"))
    if es_jurisdiccional is not None:
        stmt = stmt.where(Autoridad.es_jurisdiccional == es_jurisdiccional)
    if es_notaria is not None:
        stmt = stmt.where(Autoridad.es_notaria == es_notaria)
    if es_extinto is not None:
        stmt = stmt.where(Autoridad.es_extinto == es_extinto)
    stmt = stmt.order_by(Autoridad.clave)
    return paginate(session, stmt)
