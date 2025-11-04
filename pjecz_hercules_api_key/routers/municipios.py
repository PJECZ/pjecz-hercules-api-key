"""
Distritos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.municipios import Municipio
from ..models.permisos import Permiso
from ..schemas.municipios import MunicipioOut, OneMunicipioOut

municipios = APIRouter(prefix="/api/v5/municipios", tags=["municipios"])


@municipios.get("/{id}", response_model=OneMunicipioOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    id: int,
):
    """Detalle de una municipio a partir de su id"""
    if current_user.permissions.get("MUNICIPIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        municipio = database.query(Municipio).filter_by(id=id).one()
    except (MultipleResultsFound, NoResultFound):
        return OneMunicipioOut(success=False, message="No existe ese municipio")
    if municipio.estatus != "A":
        return OneMunicipioOut(success=False, message="No está habilitado ese municipio")
    return OneMunicipioOut(success=True, message=f"Detalle de {id}", data=MunicipioOut.model_validate(municipio))


@municipios.get("", response_model=CustomPage[MunicipioOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de municipios"""
    if current_user.permissions.get("MUNICIPIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Municipio)
    return paginate(consulta.filter_by(estatus="A").order_by(Municipio.clave))
