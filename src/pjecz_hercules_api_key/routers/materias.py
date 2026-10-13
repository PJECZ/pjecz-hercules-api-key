"""
Materias
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.schemas.materias import MateriaOut

materias = APIRouter(prefix="/api/materias")


@materias.get("", response_model=LimitOffsetPage[MateriaOut])
def materias_paginado(
    session: Annotated[Session, Depends(get_session)],
):
    """Materias paginado"""
    stmt = select(Materia).where(Materia.estatus == "A").order_by(Materia.clave)
    return paginate(session, stmt)
