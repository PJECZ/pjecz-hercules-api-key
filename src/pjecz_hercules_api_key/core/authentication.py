"""
Authentication
"""

import re
from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
from hashids import Hashids
from sqlalchemy import select
from starlette.status import HTTP_403_FORBIDDEN
from unidecode import unidecode

from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.exceptions import MyAuthenticationError
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.schemas.usuarios import UsuarioInDB

API_KEY_REGEXP = r"^\w+\.\w+\.\w+$"
X_API_KEY = APIKeyHeader(name="X-Api-Key")


def get_user(
    usuario_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> UsuarioInDB | None:
    """Consultar un usuario por su id"""
    stmt = select(Usuario).where(Usuario.id == usuario_id)
    usuario = session.execute(stmt).scalar_one_or_none()
    if usuario is None:
        return None
    return UsuarioInDB(
        id=usuario.id,
        autoridad_clave=usuario.autoridad_clave,
        autoridad_descripcion=usuario.autoridad_descripcion,
        autoridad_descripcion_corta=usuario.autoridad_descripcion_corta,
        distrito_clave=usuario.distrito_clave,
        distrito_nombre=usuario.distrito_nombre,
        distrito_nombre_corto=usuario.distrito_nombre_corto,
        oficina_clave=usuario.oficina_clave,
        oficina_descripcion=usuario.oficina_descripcion,
        oficina_descripcion_corta=usuario.oficina_descripcion_corta,
        email=usuario.email,
        nombres=usuario.nombres,
        apellido_paterno=usuario.apellido_paterno,
        apellido_materno=usuario.apellido_materno,
        puesto=usuario.puesto,
        username=usuario.email,
        permissions=usuario.permissions,
        hashed_password=usuario.contrasena if usuario.contrasena else "",
        disabled=usuario.estatus != "A",
        api_key=usuario.api_key if usuario.api_key else "",
        api_key_expiracion=usuario.api_key_expiracion if usuario.api_key_expiracion else datetime.min,
    )


def authenticate_user(
    api_key: str,
    session: Annotated[Session, Depends(get_session)],
) -> UsuarioInDB:
    """Autentificar un usuario por su api_key"""

    # Validar con expresión regular
    api_key = unidecode(api_key)
    if re.match(API_KEY_REGEXP, api_key) is None:
        raise MyAuthenticationError("No paso la validacion por expresion regular")

    # Separar el ID, el email y la cadena aleatoria del api_key
    api_key_id, api_key_email, _ = api_key.split(".")

    # Decodificar el ID
    usuario_id = Usuario.decode_id(api_key_id)
    if usuario_id is None:
        raise MyAuthenticationError("No se pudo descifrar el ID")

    # Consultar
    usuario = get_user(usuario_id, session)
    if usuario is None:
        raise MyAuthenticationError("No se encontro el usuario")

    # Validar el api_key
    if usuario.api_key != api_key:
        raise MyAuthenticationError("No es igual la api_key al dato en la base de datos")

    # Validar el email
    if api_key_email != Hashids(salt=usuario.email, min_length=8).encode(1):
        raise MyAuthenticationError("No coincide el correo electronico")

    # Validar el tiempo de expiración
    if usuario.api_key_expiracion < datetime.now():
        raise MyAuthenticationError("No vigente porque ya expiro")

    # Validad que sea activo
    if usuario.disabled:
        raise MyAuthenticationError("No es activo este usuario porque fue eliminado")

    # Entregar
    return usuario


async def get_current_active_user(
    api_key: Annotated[str, Depends(X_API_KEY)],
    session: Annotated[Session, Depends(get_session)],
) -> UsuarioInDB:
    """Obtener el usuario activo actual"""

    # Try-except
    try:
        usuario = authenticate_user(api_key, session)
    except MyAuthenticationError as error:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(error)) from error

    # Entregar
    return usuario
