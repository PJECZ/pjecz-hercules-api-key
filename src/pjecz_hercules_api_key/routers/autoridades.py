"""
Autoridades
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.schemas.autoridades import AutoridadOut

autoridades = APIRouter(prefix="/api/autoridades")


@autoridades.get("", response_model=LimitOffsetPage[AutoridadOut])
def autoridades_paginado(
    session: Annotated[Session, Depends(get_session)],
):
    """Autoridades paginado"""
    stmt = select(Autoridad).where(Autoridad.estatus == "A").order_by(Autoridad.clave)
    return paginate(session, stmt)
