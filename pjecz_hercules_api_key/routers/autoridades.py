"""
Autoridades
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.autoridades import Autoridad
from ..models.distritos import Distrito
from ..models.materias import Materia
from ..models.permisos import Permiso
from ..schemas.autoridades import AutoridadOut, OneAutoridadOut

autoridades = APIRouter(prefix="/api/v5/autoridades", tags=["autoridades"])


@autoridades.get("/{clave}", response_model=OneAutoridadOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de una autoridad a partir de su clave"""
    if current_user.permissions.get("AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        clave = safe_clave(clave)
    except ValueError:
        return OneAutoridadOut(success=False, message="No es válida la clave de la autoridad")
    try:
        autoridad = database.query(Autoridad).filter_by(clave=clave).one()
    except (MultipleResultsFound, NoResultFound):
        return OneAutoridadOut(success=False, message="No existe esa autoridad")
    if autoridad.estatus != "A":
        return OneAutoridadOut(success=False, message="No está habilitada esa autoridad")
    return OneAutoridadOut(success=True, message=f"Detalle de {clave}", data=AutoridadOut.model_validate(autoridad))


@autoridades.get("", response_model=CustomPage[AutoridadOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    distrito_clave: str = "",
    es_jurisdiccional: bool | None = None,
    es_notaria: bool | None = None,
    es_extinto: bool | None = None,
    materia_clave: str = "",
):
    """Paginado de autoridades"""
    if current_user.permissions.get("AUTORIDADES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Autoridad)
    if distrito_clave != "":
        try:
            distrito_clave = safe_clave(distrito_clave)
        except ValueError:
            return CustomPage(success=False, message="No es válida la clave del distrito")
        try:
            distrito = database.query(Distrito).filter(Distrito.clave == distrito_clave).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe ese distrito")
        if distrito.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese distrito")
        consulta = consulta.join(Distrito).filter(Distrito.clave == distrito_clave)
    if es_jurisdiccional is not None:
        consulta = consulta.filter(Autoridad.es_jurisdiccional == es_jurisdiccional)
    if es_notaria is not None:
        consulta = consulta.filter(Autoridad.es_notaria == es_notaria)
    if es_extinto is not None:
        consulta = consulta.filter(Autoridad.es_extinto == es_extinto)
    if materia_clave != "":
        try:
            materia_clave = safe_clave(materia_clave)
        except ValueError:
            return CustomPage(success=False, message="No es válida la clave de la materia")
        try:
            materia = database.query(Materia).filter(Materia.clave == materia_clave).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe esa materia")
        if materia.estatus != "A":
            return CustomPage(success=False, message="No está habilitada esa materia")
        consulta = consulta.join(Materia).filter(Materia.clave == materia_clave)
    return paginate(consulta.filter(Autoridad.estatus == "A").order_by(Autoridad.clave))
