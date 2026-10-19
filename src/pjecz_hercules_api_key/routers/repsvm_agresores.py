"""
REPSVM Agresores
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_string
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.repsvm_agresores import RepsvmAgresor
from pjecz_hercules_api_key.schemas.repsvm_agresores import RepsvmAgresorOut

repsvm_agresores = APIRouter(prefix="/repsvm_agresores")


@repsvm_agresores.get("", response_model=CustomPage[RepsvmAgresorOut])
def repsvm_agresores_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    distrito_clave: Annotated[str | None, Query()] = None,
    nombre: Annotated[str | None, Query()] = None,
):
    """REPSVM Agresores paginado"""
    if current_user.permissions.get("REPSVM AGRESORES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = (
        select(RepsvmAgresor)
        .where(RepsvmAgresor.es_publico == True)  # noqa: E712
        .where(RepsvmAgresor.estatus == "A")
    )
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        stmt = stmt.join(RepsvmAgresor.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    if nombre and (nombre := safe_string(nombre)):
        stmt = stmt.where(RepsvmAgresor.nombre.ilike(f"%{nombre}%"))
    stmt = stmt.order_by(RepsvmAgresor.id.desc())
    return paginate(session, stmt)
