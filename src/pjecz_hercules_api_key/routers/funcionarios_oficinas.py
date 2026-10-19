"""
Funcionarios Oficinas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_curp
from pjecz_hercules_api_key.models.funcionarios import Funcionario
from pjecz_hercules_api_key.models.funcionarios_oficinas import FuncionarioOficina
from pjecz_hercules_api_key.models.oficinas import Oficina
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.funcionarios_oficinas import FuncionarioOficinaOut

funcionarios_oficinas = APIRouter(prefix="/funcionarios_oficinas")


@funcionarios_oficinas.get("", response_model=CustomPage[FuncionarioOficinaOut])
def funcionarios_oficinas_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    oficina_clave: Annotated[str | None, Query()] = None,
    funcionario_curp: Annotated[str | None, Query()] = None,
):
    """Funcionarios Oficinas paginado"""
    if current_user.permissions.get("FUNCIONARIOS OFICINAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(FuncionarioOficina).where(FuncionarioOficina.estatus == "A")
    if oficina_clave and (oficina_clave := safe_clave(oficina_clave, 32)):
        stmt = stmt.join(FuncionarioOficina.oficina).where(Oficina.clave.ilike(f"%{oficina_clave}%"))
    if funcionario_curp and (funcionario_curp := safe_curp(funcionario_curp)):
        stmt = stmt.join(FuncionarioOficina.funcionario).where(Funcionario.curp.ilike(f"%{funcionario_curp}%"))
    stmt = stmt.order_by(FuncionarioOficina.id.desc())
    return paginate(session, stmt)
