"""
Funcionarios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_curp, safe_string
from pjecz_hercules_api_key.models.funcionarios import Funcionario
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.funcionarios import FuncionarioOut

funcionarios = APIRouter(prefix="/funcionarios")


@funcionarios.get("", response_model=CustomPage[FuncionarioOut])
def funcionarios_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    curp: Annotated[str | None, Query()] = None,
    nombres: Annotated[str | None, Query()] = None,
    apellido_paterno: Annotated[str | None, Query()] = None,
    apellido_materno: Annotated[str | None, Query()] = None,
):
    """Funcionarios paginado"""
    if current_user.permissions.get("FUNCIONARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Funcionario).where(Funcionario.estatus == "A")
    if curp and (curp := safe_curp(curp)):
        stmt = stmt.where(Funcionario.curp == curp)
    if nombres and (nombres := safe_string(nombres)):
        stmt = stmt.where(Funcionario.nombres.ilike(f"%{nombres}%"))
    if apellido_paterno and (apellido_paterno := safe_string(apellido_paterno)):
        stmt = stmt.where(Funcionario.apellido_paterno.ilike(f"%{apellido_paterno}%"))
    if apellido_materno and (apellido_materno := safe_string(apellido_materno)):
        stmt = stmt.where(Funcionario.apellido_materno.ilike(f"%{apellido_materno}%"))
    stmt = stmt.order_by(Funcionario.email)
    return paginate(session, stmt)
