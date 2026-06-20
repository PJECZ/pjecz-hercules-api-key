"""
Soportes Categorias
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.dependencies.safe_string import safe_string
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.soportes_categorias import SoporteCategoria
from pjecz_hercules_api_key.schemas.soportes_categorias import SoporteCategoriaOut

soportes_categorias = APIRouter(prefix="/api/v5/soportes_categorias", tags=["soportes"])


@soportes_categorias.get("", response_model=CustomPage[SoporteCategoriaOut])
async def paginado_soportes_categorias(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    departamento: str = "",
    nombre: str = "",
):
    """Paginado de Soportes Categorias"""
    if current_user.permissions.get("SOPORTES CATEGORIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(SoporteCategoria)
    if departamento != "":
        departamento = safe_string(departamento)
        if departamento not in SoporteCategoria.DEPARTAMENTOS:
            return CustomPage(success=False, message="No es válido el departamento")
        consulta = consulta.filter(SoporteCategoria.departamento == departamento)
    if nombre != "":
        nombre = safe_string(nombre, save_enie=True)
        consulta = consulta.filter(SoporteCategoria.nombre.contains(nombre))
    return paginate(consulta.filter_by(estatus="A").order_by(SoporteCategoria.nombre))
