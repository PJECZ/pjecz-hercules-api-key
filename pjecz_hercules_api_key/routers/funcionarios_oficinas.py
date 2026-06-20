"""
Funcionarios-Oficinas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.dependencies.safe_string import safe_clave, safe_curp
from pjecz_hercules_api_key.models.funcionarios import Funcionario
from pjecz_hercules_api_key.models.funcionarios_oficinas import FuncionarioOficina
from pjecz_hercules_api_key.models.oficinas import Oficina
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.funcionarios_oficinas import FuncionarioOficinaOut

funcionarios_oficinas = APIRouter(prefix="/api/v5/funcionarios_oficinas", tags=["soportes"])


@funcionarios_oficinas.get("", response_model=CustomPage[FuncionarioOficinaOut])
async def paginado_funcionarios_oficinas(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    funcionario_id: int | None = None,
    funcionario_curp: str = "",
    oficina_id: int | None = None,
    oficina_clave: str = "",
):
    """Paginado de funcionarios-oficinas"""
    if current_user.permissions.get("FUNCIONARIOS OFICINAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(FuncionarioOficina)
    if funcionario_id is not None or funcionario_curp != "":
        consulta = consulta.join(Funcionario)
        if funcionario_id is not None:
            try:
                funcionario = database.query(Funcionario).filter(Funcionario.id == funcionario_id).one()
            except MultipleResultsFound, NoResultFound:
                return CustomPage(success=False, message="No existe ese funcionario")
            if funcionario.estatus != "A":
                return CustomPage(success=False, message="No está habilitado ese funcionario")
        elif funcionario_curp != "":
            try:
                funcionario_curp = safe_curp(funcionario_curp)
            except ValueError:
                return CustomPage(success=False, message="No es válida la CURP")
            try:
                funcionario = database.query(Funcionario).filter(Funcionario.curp == funcionario_curp).one()
            except MultipleResultsFound, NoResultFound:
                return CustomPage(success=False, message="No existe ese funcionario")
            if funcionario.estatus != "A":
                return CustomPage(success=False, message="No está habilitado ese funcionario")
        consulta = consulta.filter(Funcionario.id == funcionario_id)
    if oficina_id is not None or oficina_clave != "":
        consulta = consulta.join(Oficina)
        if oficina_id is not None:
            try:
                oficina = database.query(Oficina).filter(Oficina.id == oficina_id).one()
            except MultipleResultsFound, NoResultFound:
                return CustomPage(success=False, message="No existe esa oficina")
            if oficina.estatus != "A":
                return CustomPage(success=False, message="No está habilitada esa oficina")
        elif oficina_clave != "":
            try:
                oficina_clave = safe_clave(oficina_clave)
            except ValueError:
                return CustomPage(success=False, message="No es válida la clave de la oficina")
            try:
                oficina = database.query(Oficina).filter(Oficina.clave == oficina_clave).one()
            except MultipleResultsFound, NoResultFound:
                return CustomPage(success=False, message="No existe esa oficina")
            if oficina.estatus != "A":
                return CustomPage(success=False, message="No está habilitada esa oficina")
        consulta = consulta.filter(Oficina.clave == oficina_clave)
    return paginate(consulta.filter(FuncionarioOficina.estatus == "A").order_by(FuncionarioOficina.id))
