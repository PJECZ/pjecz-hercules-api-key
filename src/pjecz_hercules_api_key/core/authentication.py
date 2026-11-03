"""
Authentication
"""

import re
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security.api_key import APIKeyHeader
from hashids import Hashids
from sqlalchemy import func, literal, not_, or_, select
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS
from unidecode import unidecode

from pjecz_hercules_api_key.config.setttings import get_settings
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.exceptions import MyAuthenticationError
from pjecz_hercules_api_key.models.bitacoras_apis import BitacoraAPI
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.schemas.usuarios import UsuarioInDB

API_KEY_REGEXP = r"^\w+\.\w+\.\w+$"
X_API_KEY = APIKeyHeader(name="X-Api-Key")

# Segmentos de ruta de las visualizaciones de PDF; se buscan con contains porque la bitácora guarda la ruta con root_path (/api/v5)
VISUALIZAR_RUTAS_PREFIJOS = (
    "/edictos/visualizar/",
    "/glosas/visualizar/",
    "/listas_de_acuerdos/visualizar/",
    "/sentencias/visualizar/",
)

settings = get_settings()


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
        autoridad_id=usuario.autoridad_id,
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
        api_key_cuota_diaria=usuario.api_key_cuota_diaria if usuario.api_key_cuota_diaria else settings.API_KEY_CUOTA_DIARIA,
        api_key_visualizaciones_por_hora=(
            usuario.api_key_visualizaciones_por_hora
            if usuario.api_key_visualizaciones_por_hora
            else settings.API_KEY_VISUALIZACIONES_POR_HORA
        ),
    )


def authenticate_user(
    api_key: str,
    session: Annotated[Session, Depends(get_session)],
    request: Request | None = None,
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

    # Identificar al usuario en la petición para que la bitácora registre los éxitos y los fallos
    if request is not None:
        request.state.usuario_id = usuario.id

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


def count_today_requests(
    usuario_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> int:
    """Contar las peticiones del usuario en el día de hoy"""
    stmt = (
        select(func.count())
        .select_from(BitacoraAPI)
        .where(BitacoraAPI.usuario_id == usuario_id)
        .where(BitacoraAPI.api_nombre == settings.API_NOMBRE)
        .where(BitacoraAPI.creado >= func.timezone(settings.TZ, func.date_trunc("day", func.timezone(settings.TZ, func.now()))))
    )
    return session.execute(stmt).scalar_one()


def count_last_hour_views(
    usuario_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> tuple[int, datetime | None]:
    """Contar las visualizaciones de PDF del usuario en los últimos 60 minutos, sin contar los 429"""
    stmt = (
        select(func.count(), func.min(BitacoraAPI.creado))
        .select_from(BitacoraAPI)
        .where(BitacoraAPI.usuario_id == usuario_id)
        .where(BitacoraAPI.api_nombre == settings.API_NOMBRE)
        .where(BitacoraAPI.creado >= func.now() - timedelta(hours=1))
        .where(or_(*[BitacoraAPI.api_ruta.contains(prefijo, autoescape=True) for prefijo in VISUALIZAR_RUTAS_PREFIJOS]))
        .where(not_(BitacoraAPI.respuesta_mensaje.startswith("429")))
    )
    conteo, mas_vieja = session.execute(stmt).one()
    return conteo, mas_vieja


async def get_current_active_user(
    request: Request,
    api_key: Annotated[str, Depends(X_API_KEY)],
    session: Annotated[Session, Depends(get_session)],
) -> UsuarioInDB:
    """Obtener el usuario activo actual"""

    # Try-except
    try:
        usuario = authenticate_user(api_key, session, request)
    except MyAuthenticationError as error:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(error)) from error

    # Validar la cuota diaria de consultas
    if count_today_requests(usuario.id, session) >= usuario.api_key_cuota_diaria:
        raise HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS, detail="Ha excedido su cuota diaria de consultas")

    # Entregar
    return usuario


async def get_current_active_user_visualizar(
    request: Request,
    api_key: Annotated[str, Depends(X_API_KEY)],
    session: Annotated[Session, Depends(get_session)],
) -> UsuarioInDB:
    """Obtener el usuario activo actual y validar su límite de visualizaciones de PDF por hora"""

    # Validar el api_key y la cuota diaria
    usuario = await get_current_active_user(request, api_key, session)

    # Validar el límite de visualizaciones en los últimos 60 minutos
    conteo, mas_vieja = count_last_hour_views(usuario.id, session)
    if conteo >= usuario.api_key_visualizaciones_por_hora:
        # Segundos para que la visualización más vieja salga de la ventana, con now() de PostgreSQL como referencia
        segundos = 3600
        if mas_vieja is not None:
            stmt = select(func.ceil(func.extract("epoch", literal(mas_vieja) + timedelta(hours=1) - func.now())))
            segundos = int(session.execute(stmt).scalar_one())
        segundos = min(max(segundos, 1), 3600)
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail="Ha excedido su límite de visualizaciones por hora",
            headers={"Retry-After": str(segundos)},
        )

    # Entregar
    return usuario
