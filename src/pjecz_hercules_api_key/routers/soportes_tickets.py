"""
Soportes Tickets
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.soportes_tickets import SoporteTicket
from pjecz_hercules_api_key.schemas.soportes_tickets import SoporteTicketOut

soportes_tickets = APIRouter(prefix="/soportes_tickets")


@soportes_tickets.get("", response_model=CustomPage[SoporteTicketOut])
def soportes_tickets_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Soportes Tickets paginado"""
    if current_user.permissions.get("SOPORTES TICKETS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(SoporteTicket).where(SoporteTicket.estatus == "A").order_by(SoporteTicket.id.desc())
    return paginate(session, stmt)
