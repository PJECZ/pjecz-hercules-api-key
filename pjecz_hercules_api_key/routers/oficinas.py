"""
Oficinas
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
from pjecz_hercules_api_key.models.domicilios import Domicilio
from pjecz_hercules_api_key.models.oficinas import Oficina
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.oficinas import OficinaOut

oficinas = APIRouter(prefix="/api/v5/oficinas", tags=["oficinas"])


@oficinas.get("", response_model=CustomPage[OficinaOut])
async def paginado_oficinas(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    distrito_clave: str = "",
    domicilio_id: int | None = None,
):
    """Paginado de oficinas"""
    if current_user.permissions.get("OFICINAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Oficina)
    if distrito_clave != "":
        try:
            distrito_clave = safe_clave(distrito_clave)
        except ValueError:
            return CustomPage(success=False, message="No es válida la clave del distrito")
        try:
            distrito = database.query(Distrito).filter(Distrito.clave == distrito_clave).one()
        except MultipleResultsFound, NoResultFound:
            return CustomPage(success=False, message="No existe ese distrito")
        if distrito.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese distrito")
        consulta = consulta.join(Distrito).filter(Distrito.clave == distrito_clave)
    if domicilio_id is not None:
        try:
            domicilio = database.query(Domicilio).filter(Domicilio.id == domicilio_id).one()
        except MultipleResultsFound, NoResultFound:
            return CustomPage(success=False, message="No existe ese domicilio")
        if domicilio.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese domicilio")
        consulta = consulta.join(Domicilio).filter(Domicilio.id == domicilio_id)
    return paginate(consulta.filter(Oficina.estatus == "A").order_by(Oficina.clave))
