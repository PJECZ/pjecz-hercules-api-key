"""
Soportes Tickets
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_curp, safe_email, safe_string
from pjecz_hercules_api_key.models.funcionarios import Funcionario
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.soportes_categorias import SoporteCategoria
from pjecz_hercules_api_key.models.soportes_tickets import SoporteTicket
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.schemas.soportes_tickets import SoporteTicketOut

soportes_tickets = APIRouter(prefix="/soportes_tickets")


@soportes_tickets.get("", response_model=CustomPage[SoporteTicketOut])
def soportes_tickets_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    estado: Annotated[str | None, Query()] = None,
    funcionario_curp: Annotated[str | None, Query()] = None,
    soporte_categoria_nombre: Annotated[str | None, Query()] = None,
    usuario_email: Annotated[str | None, Query()] = None,
):
    """Soportes Tickets paginado"""
    if current_user.permissions.get("SOPORTES TICKETS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(SoporteTicket).where(SoporteTicket.estatus == "A")
    if estado and (estado := safe_string(estado)):
        if estado not in SoporteTicket.ESTADOS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="El estado no es válido")
        stmt = stmt.where(SoporteTicket.estado == estado)
    if funcionario_curp and (funcionario_curp := safe_curp(funcionario_curp)):
        stmt = stmt.join(SoporteTicket.funcionario).where(Funcionario.curp.ilike(f"%{funcionario_curp}%"))
    if soporte_categoria_nombre and (soporte_categoria_nombre := safe_string(soporte_categoria_nombre)):
        stmt = stmt.join(SoporteTicket.soporte_categoria).where(SoporteCategoria.nombre.ilike(f"%{soporte_categoria_nombre}%"))
    if usuario_email and (usuario_email := safe_email(usuario_email)):
        stmt = stmt.join(SoporteTicket.usuario).where(Usuario.email.ilike(f"%{usuario_email}%"))
    stmt = stmt.order_by(SoporteTicket.id.desc())
    return paginate(session, stmt)
