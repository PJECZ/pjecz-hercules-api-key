"""
Bitacoras Apis
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..config.settings import Settings, get_settings
from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_email, safe_string
from ..models.bitacoras_apis import BitacoraAPI
from ..models.permisos import Permiso
from ..models.usuarios import Usuario
from ..schemas.bitacoras_apis import BitacoraAPIOut

PREFIX = "/api/v5/bitacoras_apis"
bitacoras_apis = APIRouter(prefix=PREFIX, tags=["usuarios"])


@bitacoras_apis.get("", response_model=CustomPage[BitacoraAPIOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    apellido_paterno: str = "",
    apellido_materno: str = "",
    email: str = "",
    nombres: str = "",
):
    """Paginado de Bitacoras Apis"""
    if current_user.permissions.get("BITACORAS APIS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(BitacoraAPI).join(Usuario)
    if apellido_paterno != "":
        apellido_paterno = safe_string(apellido_paterno)
        if apellido_paterno != "":
            consulta = consulta.filter(Usuario.apellido_paterno.contains(apellido_paterno))
            respuestas_mensajes.append(f"Apellido paterno: {apellido_paterno}")
    if apellido_materno != "":
        apellido_materno = safe_string(apellido_materno)
        if apellido_materno != "":
            consulta = consulta.filter(Usuario.apellido_materno.contains(apellido_materno))
            respuestas_mensajes.append(f"Apellido materno: {apellido_materno}")
    if email != "":
        try:
            email = str(safe_email(email, search_fragment=True))
        except ValueError:
            return CustomPage(success=False, message="No es válido el email")
        consulta = consulta.filter(Usuario.email.contains(email))
        respuestas_mensajes.append(f"Email: {email}")
    if nombres != "":
        nombres = safe_string(nombres)
        if nombres != "":
            consulta = consulta.filter(Usuario.nombres.contains(nombres))
            respuestas_mensajes.append(f"Nombres: {nombres}")
    bitacora_api = BitacoraAPI(
        usuario_id=current_user.id,
        api_nombre=settings.API_NOMBRE,
        api_ruta=PREFIX,
        peticion="GET",
        respuesta_mensaje=safe_string(", ".join(respuestas_mensajes), save_enie=True, to_uppercase=False),
    )
    database.add(bitacora_api)
    database.commit()
    return paginate(consulta.order_by(BitacoraAPI.id.desc()))
