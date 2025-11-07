"""
Municipios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.estados import Estado
from ..models.municipios import Municipio
from ..models.permisos import Permiso
from ..schemas.municipios import MunicipioOut

municipios = APIRouter(prefix="/api/v5/municipios", tags=["municipios"])


@municipios.get("", response_model=CustomPage[MunicipioOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    estado_clave: str | None = None,
):
    """Paginado de municipios"""
    if current_user.permissions.get("MUNICIPIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Municipio)
    if estado_clave is not None:
        try:
            estado_clave = safe_clave(estado_clave)
        except ValueError:
            return CustomPage(success=False, message="No es válida la clave del estado")
        try:
            estado = database.query(Estado).filter(Estado.clave == estado_clave).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe ese estado")
        if estado.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese estado")
        consulta = consulta.join(Estado).filter(Estado.clave == estado_clave)
    return paginate(consulta.filter_by(estatus="A").order_by(Municipio.clave))
