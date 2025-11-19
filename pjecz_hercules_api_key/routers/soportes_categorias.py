"""
Soportes Categorias
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_string
from ..models.permisos import Permiso
from ..models.soportes_categorias import SoporteCategoria
from ..schemas.soportes_categorias import SoporteCategoriaOut

soportes_categorias = APIRouter(prefix="/api/v5/soportes_categorias", tags=["soportes"])


@soportes_categorias.get("", response_model=CustomPage[SoporteCategoriaOut])
async def paginado_soportes_categorias(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    departamento: str | None = None,
    nombre: str | None = None,
):
    """Paginado de Soportes Categorias"""
    if current_user.permissions.get("SOPORTES CATEGORIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(SoporteCategoria)
    if departamento is not None:
        departamento = safe_string(departamento)
        if departamento not in SoporteCategoria.DEPARTAMENTOS:
            return CustomPage(success=False, message="No es válido el departamento")
        consulta = consulta.filter(SoporteCategoria.departamento == departamento)
    if nombre is not None:
        nombre = safe_string(nombre)
        consulta = consulta.filter(SoporteCategoria.nombre.contains(nombre))
    return paginate(consulta.filter_by(estatus="A").order_by(SoporteCategoria.nombre))
