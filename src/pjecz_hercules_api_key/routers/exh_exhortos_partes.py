"""
EXH Exhortos Partes
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_string
from pjecz_hercules_api_key.models.exh_exhortos_partes import ExhExhortoParte
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.exh_exhortos_partes import ExhExhortoParteOut

exh_exhortos_partes = APIRouter(prefix="/exh_exhortos_partes")


@exh_exhortos_partes.get("", response_model=CustomPage[ExhExhortoParteOut])
def exh_exhortos_partes_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    nombre: Annotated[str | None, Query()] = None,
    apellido_paterno: Annotated[str | None, Query()] = None,
    apellido_materno: Annotated[str | None, Query()] = None,
):
    """EXH Exhortos Partes paginado"""
    if current_user.permissions.get("EXH EXHORTOS PARTES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ExhExhortoParte).where(ExhExhortoParte.estatus == "A")
    if nombre and (nombre := safe_string(nombre)):
        stmt = stmt.where(ExhExhortoParte.nombre.ilike(f"%{nombre}%"))
    if apellido_paterno and (apellido_paterno := safe_string(apellido_paterno)):
        stmt = stmt.where(ExhExhortoParte.apellido_paterno.ilike(f"%{apellido_paterno}%"))
    if apellido_materno and (apellido_materno := safe_string(apellido_materno)):
        stmt = stmt.where(ExhExhortoParte.apellido_materno.ilike(f"%{apellido_materno}%"))
    stmt = stmt.order_by(ExhExhortoParte.id.desc())
    return paginate(session, stmt)
