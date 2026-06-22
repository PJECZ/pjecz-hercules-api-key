"""
Distritos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.dependencies.safe_string import safe_clave
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.distritos import DistritoOut, OneDistritoOut

distritos = APIRouter(prefix="/api/v5/distritos", tags=["distritos"])


@distritos.get("/{clave}", response_model=OneDistritoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de una distrito a partir de su clave"""
    if current_user.permissions.get("DISTRITOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        clave = safe_clave(clave)
    except ValueError:
        return OneDistritoOut(success=False, message="No es válida la clave del distrito")
    try:
        distrito = database.query(Distrito).filter_by(clave=clave).one()
    except MultipleResultsFound, NoResultFound:
        return OneDistritoOut(success=False, message="No existe ese distrito")
    if distrito.estatus != "A":
        return OneDistritoOut(success=False, message="No está habilitado ese distrito")
    return OneDistritoOut(success=True, message=f"Detalle de {clave}", data=DistritoOut.model_validate(distrito))


@distritos.get("", response_model=CustomPage[DistritoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    es_distrito: bool | None = None,
    es_jurisdiccional: bool | None = None,
):
    """Paginado de distritos"""
    if current_user.permissions.get("DISTRITOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Distrito)
    if es_distrito is not None:
        consulta = consulta.filter_by(es_distrito=es_distrito)
    if es_jurisdiccional is not None:
        consulta = consulta.filter_by(es_jurisdiccional=es_jurisdiccional)
    return paginate(consulta.filter_by(estatus="A").order_by(Distrito.clave))
