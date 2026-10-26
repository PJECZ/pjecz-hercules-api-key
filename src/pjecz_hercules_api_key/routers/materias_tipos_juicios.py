"""
Materias Tipos de Juicios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_string
from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.materias_tipos_juicios import MateriaTipoJuicioOut

materias_tipos_juicios = APIRouter(prefix="/materias_tipos_juicios")


@materias_tipos_juicios.get("", response_model=CustomPage[MateriaTipoJuicioOut])
def materias_tipos_juicios_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    materia_clave: Annotated[str | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
):
    """Materias Tipos de Juicios paginado"""
    if current_user.permissions.get("MATERIAS TIPOS JUICIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(MateriaTipoJuicio).where(MateriaTipoJuicio.estatus == "A")
    if materia_clave and (materia_clave := safe_clave(materia_clave)):
        stmt = stmt.join(MateriaTipoJuicio.materia).where(Materia.clave.ilike(f"%{materia_clave}%"))
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(MateriaTipoJuicio.descripcion.ilike(f"%{descripcion}%"))
    stmt = stmt.order_by(MateriaTipoJuicio.id.desc())
    return paginate(session, stmt)
