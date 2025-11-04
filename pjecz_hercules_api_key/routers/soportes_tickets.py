"""
Soportes Tickets
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..models.permisos import Permiso
from ..models.soportes_categorias import SoporteCategoria
from ..models.soportes_tickets import SoporteTicket
from ..schemas.soportes_tickets import SoporteTicketOut

soportes_tickets = APIRouter(prefix="/api/v5/soportes_tickets", tags=["soportes"])


@soportes_tickets.get("", response_model=CustomPage[SoporteTicketOut])
async def paginado_soportes_tickets(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de Soportes Tickets"""
    if current_user.permissions.get("SOPORTES TICKETS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return paginate(database.query(SoporteTicket).filter(SoporteTicket.estatus == "A").order_by(SoporteTicket.edificio))
