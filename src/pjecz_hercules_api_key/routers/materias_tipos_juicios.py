"""
Materias Tipos de Juicios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.materias_tipos_juicios import MateriaTipoJuicioOut

materias_tipos_juicios = APIRouter(prefix="/api/materias_tipos_juicios")


@materias_tipos_juicios.get("", response_model=LimitOffsetPage[MateriaTipoJuicioOut])
def materias_tipos_juicios_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Materias Tipos de Juicios paginado"""
    if current_user.permissions.get("MATERIAS TIPOS JUICIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(MateriaTipoJuicio).where(MateriaTipoJuicio.estatus == "A").order_by(MateriaTipoJuicio.id.desc())
    return paginate(session, stmt)
