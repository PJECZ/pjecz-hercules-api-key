"""
Funcionarios-Oficinas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.funcionarios import Funcionario
from ..models.funcionarios_oficinas import FuncionarioOficina
from ..models.oficinas import Oficina
from ..models.permisos import Permiso
from ..schemas.funcionarios_oficinas import FuncionarioOficinaOut

funcionarios_oficinas = APIRouter(prefix="/api/v5/funcionarios_oficinas", tags=["soportes"])


@funcionarios_oficinas.get("", response_model=CustomPage[FuncionarioOficinaOut])
async def paginado_funcionarios_oficinas(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    funcionario_id: int | None = None,
    oficina_id: int | None = None,
    oficina_clave: str | None = None,
):
    """Paginado de funcionarios-oficinas"""
    if current_user.permissions.get("FUNCIONARIOS OFICINAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(FuncionarioOficina)
    if funcionario_id is not None:
        consulta = consulta.join(Funcionario).filter(Funcionario.id == funcionario_id).filter(Funcionario.estatus == "A")
    if oficina_id is not None or oficina_clave is not None:
        consulta = consulta.join(Oficina)
    if oficina_clave is not None:
        try:
            oficina_clave = safe_clave(oficina_clave)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
        consulta = consulta.filter(Oficina.clave == oficina_clave).filter(Oficina.estatus == "A")
    if oficina_id is not None:
        consulta = consulta.filter(Oficina.id == oficina_id).filter(Oficina.estatus == "A")
    return paginate(consulta.filter(FuncionarioOficina.estatus == "A").order_by(FuncionarioOficina.id))
