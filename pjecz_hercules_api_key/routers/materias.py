"""
Materias
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.dependencies.safe_string import safe_clave
from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.materias import MateriaOut, OneMateriaOut

materias = APIRouter(prefix="/api/v5/materias", tags=["materias"])


@materias.get("/{clave}", response_model=OneMateriaOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de una materia a partir de su clave"""
    if current_user.permissions.get("MATERIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        clave = safe_clave(clave)
    except ValueError:
        return OneMateriaOut(success=False, message="No es válida la clave de la materia")
    try:
        materia = database.query(Materia).filter_by(clave=clave).one()
    except MultipleResultsFound, NoResultFound:
        return OneMateriaOut(success=False, message="No existe esa materia")
    if materia.estatus != "A":
        return OneMateriaOut(success=False, message="No está habilitado esa materia")
    return OneMateriaOut(success=True, message=f"Detalle de {clave}", data=MateriaOut.model_validate(materia))


@materias.get("", response_model=CustomPage[MateriaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    en_sentencias: bool | None = None,
    en_exh_exhortos: bool | None = None,
):
    """Paginado de materias"""
    if current_user.permissions.get("MATERIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Materia)
    if en_sentencias is not None:
        consulta = consulta.filter(Materia.en_sentencias == en_sentencias)
    if en_exh_exhortos is not None:
        consulta = consulta.filter(Materia.en_exh_exhortos == en_exh_exhortos)
    return paginate(consulta.filter_by(estatus="A").order_by(Materia.nombre))
