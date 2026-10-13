"""
Distritos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.schemas.distritos import DistritoOut

distritos = APIRouter(prefix="/api/distritos")


@distritos.get("", response_model=LimitOffsetPage[DistritoOut])
def distritos_paginado(
    session: Annotated[Session, Depends(get_session)],
):
    """Distritos paginado"""
    stmt = select(Distrito).where(Distrito.estatus == "A").order_by(Distrito.clave)
    return paginate(session, stmt)
