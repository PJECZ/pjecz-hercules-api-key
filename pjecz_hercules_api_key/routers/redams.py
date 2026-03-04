"""
REDAMS
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..config.settings import Settings, get_settings
from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_string
from ..models.autoridades import Autoridad
from ..models.bitacoras_apis import BitacoraAPI
from ..models.distritos import Distrito
from ..models.permisos import Permiso
from ..models.redams import Redam
from ..schemas.redams import RedamOut

PREFIX = "/api/v5/redams"
redams = APIRouter(prefix=PREFIX, tags=["redam"])


@redams.get("", response_model=CustomPage[RedamOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    autoridad_clave: str = "",
    distrito_clave: str = "",
    nombre: str = "",
):
    """Paginado de REDAMs"""
    if current_user.permissions.get("REDAMS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(Redam)
    if distrito_clave == "" and autoridad_clave != "":
        try:
            autoridad_clave = safe_clave(autoridad_clave)
        except ValueError:
            return CustomPage(success=False, message="No es válida la clave de la autoridad")
        try:
            autoridad = database.query(Autoridad).filter(Autoridad.clave == autoridad_clave).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe esa autoridad")
        if autoridad.estatus != "A":
            return CustomPage(success=False, message="No está habilitada esa autoridad")
        consulta = consulta.join(Autoridad).filter(Autoridad.clave == autoridad_clave)
        respuestas_mensajes.append(f"Autoridad: {autoridad_clave}")
    elif distrito_clave != "" and autoridad_clave == "":
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
        consulta = consulta.join(Distrito).join(Autoridad).filter(Distrito.clave == distrito_clave)
        respuestas_mensajes.append(f"Distrito: {distrito_clave}")
    if nombre != "":
        nombre = safe_string(nombre, save_enie=True)
        if nombre != "":
            consulta = consulta.filter(Redam.nombre.contains(nombre))
            respuestas_mensajes.append(f"Nombre: {nombre}")
    bitacora_api = BitacoraAPI(
        usuario_id=current_user.id,
        api_nombre=settings.API_NOMBRE,
        api_ruta=PREFIX,
        peticion="GET",
        respuesta_mensaje=safe_string(", ".join(respuestas_mensajes), save_enie=True, to_uppercase=False),
    )
    database.add(bitacora_api)
    database.commit()
    return paginate(consulta.filter(Redam.estatus == "A").order_by(Redam.nombre))
