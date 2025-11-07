"""
Funcionarios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..models.funcionarios import Funcionario
from ..models.permisos import Permiso
from ..schemas.funcionarios import FuncionarioOut

funcionarios = APIRouter(prefix="/api/v5/funcionarios", tags=["soportes"])


@funcionarios.get("", response_model=CustomPage[FuncionarioOut])
async def paginado_funcionarios(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de funcionarios"""
    if current_user.permissions.get("FUNCIONARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return paginate(
        database.query(Funcionario)
        .filter(Funcionario.estatus == "A")
        .order_by(Funcionario.nombres, Funcionario.apellido_paterno, Funcionario.apellido_materno)
    )
