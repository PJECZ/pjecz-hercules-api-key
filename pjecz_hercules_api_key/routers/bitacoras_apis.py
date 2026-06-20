"""
Bitacoras Apis
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Date

from pjecz_hercules_api_key.config.settings import Settings, get_settings
from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.dependencies.safe_string import safe_email, safe_string
from pjecz_hercules_api_key.models.bitacoras_apis import BitacoraAPI
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.schemas.bitacoras_apis import BitacoraAPIOut

PREFIX = "/api/v5/bitacoras_apis"
bitacoras_apis = APIRouter(prefix=PREFIX, tags=["usuarios"])


@bitacoras_apis.get("", response_model=CustomPage[BitacoraAPIOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    api_nombre: str = "",
    api_ruta: str = "",
    creado: date | None = None,
    creado_desde: date | None = None,
    creado_hasta: date | None = None,
    email: str = "",
    peticion: str = "",
):
    """Paginado de Bitacoras Apis"""
    if current_user.permissions.get("BITACORAS APIS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(BitacoraAPI).join(Usuario)
    if api_nombre != "":
        consulta = consulta.filter(BitacoraAPI.api_nombre == api_nombre)
        respuestas_mensajes.append(f"API nombre: {api_nombre}")
    if api_ruta != "":
        consulta = consulta.filter(BitacoraAPI.api_ruta == api_ruta)
        respuestas_mensajes.append(f"API ruta: {api_ruta}")
    if creado is not None:
        consulta = consulta.filter(BitacoraAPI.creado.cast(Date) == creado)
        respuestas_mensajes.append(f"Creado: {creado}")
    if creado_desde is not None:
        consulta = consulta.filter(BitacoraAPI.creado.cast(Date) >= creado_desde)
        respuestas_mensajes.append(f"Creado desde: {creado_desde}")
    if creado_hasta is not None:
        consulta = consulta.filter(BitacoraAPI.creado.cast(Date) <= creado_hasta)
        respuestas_mensajes.append(f"Creado hasta: {creado_hasta}")
    if email != "":
        try:
            email = str(safe_email(email, search_fragment=True))
        except ValueError:
            return CustomPage(success=False, message="No es válido el email")
        consulta = consulta.filter(Usuario.email.contains(email))
        respuestas_mensajes.append(f"Email: {email}")
    if peticion != "":
        peticion = safe_string(peticion)
        if peticion in BitacoraAPI.ESTADOS:
            consulta = consulta.filter(BitacoraAPI.peticion == peticion)
            respuestas_mensajes.append(f"Peticion: {peticion}")
        else:
            return CustomPage(success=False, message="No es válido el estado")
    bitacora_api = BitacoraAPI(
        usuario_id=current_user.id,
        api_nombre=settings.API_NOMBRE,
        api_ruta=PREFIX,
        peticion="GET",
        respuesta_mensaje=safe_string(", ".join(respuestas_mensajes), save_enie=True, to_uppercase=False),
        respuesta_datos={"total": consulta.count()},
    )
    database.add(bitacora_api)
    database.commit()
    return paginate(consulta.order_by(BitacoraAPI.id.desc()))
