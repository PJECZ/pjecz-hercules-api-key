"""
Soportes Tickets
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_curp, safe_email, safe_string
from ..models.funcionarios import Funcionario
from ..models.permisos import Permiso
from ..models.soportes_categorias import SoporteCategoria
from ..models.soportes_tickets import SoporteTicket
from ..models.usuarios import Usuario
from ..schemas.soportes_tickets import SoporteTicketOut

soportes_tickets = APIRouter(prefix="/api/v5/soportes_tickets", tags=["soportes"])


@soportes_tickets.get("", response_model=CustomPage[SoporteTicketOut])
async def paginado_soportes_tickets(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    creado: date | None = None,
    creado_desde: date | None = None,
    creado_hasta: date | None = None,
    funcionario_id: int | None = None,
    funcionario_curp: str | None = None,
    modificado: date | None = None,
    modificado_desde: date | None = None,
    modificado_hasta: date | None = None,
    soporte_categoria_id: int | None = None,
    soporte_categoria_nombre: str | None = None,
    usuario_email: str | None = None,
):
    """Paginado de Soportes Tickets"""
    if current_user.permissions.get("SOPORTES TICKETS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(SoporteTicket)
    if funcionario_id is not None or funcionario_curp is not None:
        consulta = consulta.join(Funcionario)
        if funcionario_id is not None:
            try:
                funcionario = database.query(Funcionario).filter(Funcionario.id == funcionario_id).one()
            except (MultipleResultsFound, NoResultFound):
                return CustomPage(success=False, message="No existe ese funcionario")
            if funcionario.estatus != "A":
                return CustomPage(success=False, message="No está habilitado ese funcionario")
        elif funcionario_curp is not None:
            try:
                funcionario_curp = safe_curp(funcionario_curp)
            except ValueError:
                return CustomPage(success=False, message="No es válida la CURP")
            try:
                funcionario = database.query(Funcionario).filter(Funcionario.curp == funcionario_curp).one()
            except (MultipleResultsFound, NoResultFound):
                return CustomPage(success=False, message="No existe ese funcionario")
            if funcionario.estatus != "A":
                return CustomPage(success=False, message="No está habilitado ese funcionario")
        consulta = consulta.filter(Funcionario.id == funcionario_id)
    if soporte_categoria_id is not None or soporte_categoria_nombre is not None:
        consulta = consulta.join(SoporteCategoria)
        if soporte_categoria_id is not None:
            try:
                soporte_categoria = database.query(SoporteCategoria).filter(SoporteCategoria.id == soporte_categoria_id).one()
            except (MultipleResultsFound, NoResultFound):
                return CustomPage(success=False, message="No existe esa categoría de soporte")
            if soporte_categoria.estatus != "A":
                return CustomPage(success=False, message="No está habilitada esa categoría de soporte")
        elif soporte_categoria_nombre is not None:
            try:
                soporte_categoria_nombre = safe_string(soporte_categoria_nombre)
            except ValueError:
                return CustomPage(success=False, message="No es válido el nombre de la categoría de soporte")
            try:
                soporte_categoria = (
                    database.query(SoporteCategoria).filter(SoporteCategoria.nombre == soporte_categoria_nombre).one()
                )
            except (MultipleResultsFound, NoResultFound):
                return CustomPage(success=False, message="No existe esa categoría de soporte")
            if soporte_categoria.estatus != "A":
                return CustomPage(success=False, message="No está habilitada esa categoría de soporte")
        consulta = consulta.filter(SoporteCategoria.id == soporte_categoria_id)
    if usuario_email is not None:
        try:
            usuario_email = safe_email(usuario_email)
        except ValueError:
            return CustomPage(success=False, message="No es válido el email")
        try:
            usuario = database.query(Usuario).filter(Usuario.email == usuario_email).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe ese usuario")
        if usuario.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese usuario")
        consulta = consulta.join(Usuario).filter(Usuario.email == usuario_email)
    return paginate(consulta.filter(SoporteTicket.estatus == "A").order_by(SoporteTicket.edificio))
