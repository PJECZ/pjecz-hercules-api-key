"""
Oficios Documentos
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Date

from ..config.settings import Settings, get_settings
from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_email, safe_string
from ..models.autoridades import Autoridad
from ..models.bitacoras_apis import BitacoraAPI
from ..models.ofi_documentos import OfiDocumento
from ..models.ofi_documentos_destinatarios import OfiDocumentoDestinatario
from ..models.permisos import Permiso
from ..models.usuarios import Usuario
from ..schemas.ofi_documentos import OfiDocumentoOut

PREFIX = "/api/v5/ofi_documentos"
ofi_documentos = APIRouter(prefix=PREFIX, tags=["oficios"])


@ofi_documentos.get("/mi_autoridad", response_model=CustomPage[OfiDocumentoOut])
async def mi_autoridad(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    anio: int | None = None,
    creado: date | None = None,
    creado_desde: date | None = None,
    creado_hasta: date | None = None,
    descripcion: str = "",
    estado: str = "",
    folio: str = "",
    numero: int | None = None,
    usuario_email: str = "",
):
    """Paginado de mi autoridad"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(OfiDocumento).join(Usuario).join(Autoridad)
    if anio is not None:
        consulta = consulta.filter(OfiDocumento.folio_anio == anio)
        respuestas_mensajes.append(f"Año: {anio}")
    if creado is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) == creado)
        respuestas_mensajes.append(f"Creado: {creado}")
    if creado_desde is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) >= creado_desde)
        respuestas_mensajes.append(f"Creado desde: {creado_desde}")
    if creado_hasta is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) <= creado_hasta)
        respuestas_mensajes.append(f"Creado hasta: {creado_hasta}")
    if descripcion != "":
        descripcion = safe_string(descripcion, save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(OfiDocumento.descripcion.contains(descripcion))
            respuestas_mensajes.append(f"Descripción: {descripcion}")
    if estado != "":
        estado = safe_string(estado)
        if estado in OfiDocumento.ESTADOS:
            consulta = consulta.filter(OfiDocumento.estado == estado)
            respuestas_mensajes.append(f"Estado: {estado}")
        else:
            return CustomPage(success=False, message="No es válido el estado")
    if folio != "":
        folio = safe_string(folio)
        if folio != "":
            consulta = consulta.filter(OfiDocumento.folio.contains(folio))
            respuestas_mensajes.append(f"Folio: {folio}")
    if numero is not None:
        consulta = consulta.filter(OfiDocumento.folio_num == numero)
        respuestas_mensajes.append(f"Folio número: {numero}")
    if usuario_email != "":
        try:
            usuario_email = safe_email(usuario_email, search_fragment=True)
        except ValueError:
            return CustomPage(success=False, message="El usuario_email no es válido")
        consulta = consulta.filter(Usuario.email.contains(usuario_email))
        respuestas_mensajes.append(f"Usuario email: {usuario_email}")
    consulta = consulta.filter(Autoridad.id == current_user.autoridad_id)
    consulta = consulta.filter(OfiDocumento.estatus == "A")
    bitacora_api = BitacoraAPI(
        usuario_id=current_user.id,
        api_nombre=settings.API_NOMBRE,
        api_ruta=f"{PREFIX}/mi_autoridad",
        peticion="GET",
        respuesta_mensaje=safe_string(", ".join(respuestas_mensajes), save_enie=True, to_uppercase=False),
        respuesta_datos={"total": consulta.count()},
    )
    database.add(bitacora_api)
    database.commit()
    return paginate(consulta.order_by(OfiDocumento.creado.desc()))


@ofi_documentos.get("/mi_bandeja_de_entrada", response_model=CustomPage[OfiDocumentoOut])
async def mi_bandeja_de_entrada(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    anio: int | None = None,
    creado: date | None = None,
    creado_desde: date | None = None,
    creado_hasta: date | None = None,
    descripcion: str = "",
    estado: str = "",
    folio: str = "",
    numero: int | None = None,
    usuario_email: str = "",
):
    """Paginado de mi bandeja de entrada, es decir, aquellos en los que el usuario es destinatario"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(OfiDocumento).join(OfiDocumentoDestinatario)
    if anio is not None:
        consulta = consulta.filter(OfiDocumento.folio_anio == anio)
        respuestas_mensajes.append(f"Año: {anio}")
    if creado is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) == creado)
        respuestas_mensajes.append(f"Creado: {creado}")
    if creado_desde is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) >= creado_desde)
        respuestas_mensajes.append(f"Creado desde: {creado_desde}")
    if creado_hasta is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) <= creado_hasta)
        respuestas_mensajes.append(f"Creado hasta: {creado_hasta}")
    if descripcion != "":
        descripcion = safe_string(descripcion, save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(OfiDocumento.descripcion.contains(descripcion))
            respuestas_mensajes.append(f"Descripción: {descripcion}")
    if estado != "":
        estado = safe_string(estado)
        if estado in OfiDocumento.ESTADOS:
            consulta = consulta.filter(OfiDocumento.estado == estado)
            respuestas_mensajes.append(f"Estado: {estado}")
        else:
            return CustomPage(success=False, message="No es válido el estado")
    if folio != "":
        folio = safe_string(folio)
        if folio != "":
            consulta = consulta.filter(OfiDocumento.folio.contains(folio))
            respuestas_mensajes.append(f"Folio: {folio}")
    if numero is not None:
        consulta = consulta.filter(OfiDocumento.folio_num == numero)
        respuestas_mensajes.append(f"Folio número: {numero}")
    if usuario_email != "":
        try:
            usuario_email = safe_email(usuario_email, search_fragment=True)
        except ValueError:
            return CustomPage(success=False, message="El usuario_email no es válido")
        consulta = consulta.join(Usuario, OfiDocumento.usuario_id == Usuario.id).filter(Usuario.email.contains(usuario_email))
        respuestas_mensajes.append(f"Usuario email: {usuario_email}")
    consulta = consulta.filter(OfiDocumentoDestinatario.usuario_id == current_user.id)
    consulta = consulta.filter(OfiDocumentoDestinatario.estatus == "A")
    consulta = consulta.filter(OfiDocumento.estatus == "A")
    bitacora_api = BitacoraAPI(
        usuario_id=current_user.id,
        api_nombre=settings.API_NOMBRE,
        api_ruta=f"{PREFIX}/mi_bandeja_de_entrada",
        peticion="GET",
        respuesta_mensaje=safe_string(", ".join(respuestas_mensajes), save_enie=True, to_uppercase=False),
        respuesta_datos={"total": consulta.count()},
    )
    database.add(bitacora_api)
    database.commit()
    return paginate(consulta.order_by(OfiDocumento.creado.desc()))


@ofi_documentos.get("/mis_oficios", response_model=CustomPage[OfiDocumentoOut])
async def mis_oficios(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    anio: int | None = None,
    creado: date | None = None,
    creado_desde: date | None = None,
    creado_hasta: date | None = None,
    descripcion: str = "",
    estado: str = "",
    folio: str = "",
    numero: int | None = None,
):
    """Paginado de mis oficios"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(OfiDocumento)
    if anio is not None:
        consulta = consulta.filter(OfiDocumento.folio_anio == anio)
        respuestas_mensajes.append(f"Año: {anio}")
    if creado is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) == creado)
        respuestas_mensajes.append(f"Creado: {creado}")
    if creado_desde is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) >= creado_desde)
        respuestas_mensajes.append(f"Creado desde: {creado_desde}")
    if creado_hasta is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) <= creado_hasta)
        respuestas_mensajes.append(f"Creado hasta: {creado_hasta}")
    if descripcion != "":
        descripcion = safe_string(descripcion, save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(OfiDocumento.descripcion.contains(descripcion))
            respuestas_mensajes.append(f"Descripción: {descripcion}")
    if estado != "":
        estado = safe_string(estado)
        if estado in OfiDocumento.ESTADOS:
            consulta = consulta.filter(OfiDocumento.estado == estado)
            respuestas_mensajes.append(f"Estado: {estado}")
        else:
            return CustomPage(success=False, message="No es válido el estado")
    if folio != "":
        folio = safe_string(folio)
        if folio != "":
            consulta = consulta.filter(OfiDocumento.folio.contains(folio))
            respuestas_mensajes.append(f"Folio: {folio}")
    if numero is not None:
        consulta = consulta.filter(OfiDocumento.folio_num == numero)
        respuestas_mensajes.append(f"Folio número: {numero}")
    consulta = consulta.filter(OfiDocumento.usuario_id == current_user.id)
    consulta = consulta.filter(OfiDocumento.estatus == "A")
    bitacora_api = BitacoraAPI(
        usuario_id=current_user.id,
        api_nombre=settings.API_NOMBRE,
        api_ruta=f"{PREFIX}/mis_oficios",
        peticion="GET",
        respuesta_mensaje=safe_string(", ".join(respuestas_mensajes), save_enie=True, to_uppercase=False),
        respuesta_datos={"total": consulta.count()},
    )
    database.add(bitacora_api)
    database.commit()
    return paginate(consulta.order_by(OfiDocumento.creado.desc()))


@ofi_documentos.get("", response_model=CustomPage[OfiDocumentoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    anio: int | None = None,
    autoridad_clave: str = "",
    creado: date | None = None,
    creado_desde: date | None = None,
    creado_hasta: date | None = None,
    descripcion: str = "",
    estado: str = "",
    folio: str = "",
    numero: int | None = None,
    usuario_email: str = "",
):
    """Paginado de todos los oficios"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(OfiDocumento).join(Usuario).join(Autoridad)
    if anio is not None:
        consulta = consulta.filter(OfiDocumento.folio_anio == anio)
    if autoridad_clave != "":
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave != "":
            consulta = consulta.filter(Autoridad.clave.contains(autoridad_clave))
            respuestas_mensajes.append(f"Autoridad: {autoridad_clave}")
    if creado is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) == creado)
        respuestas_mensajes.append(f"Creado: {creado}")
    if creado_desde is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) >= creado_desde)
        respuestas_mensajes.append(f"Creado desde: {creado_desde}")
    if creado_hasta is not None:
        consulta = consulta.filter(OfiDocumento.creado.cast(Date) <= creado_hasta)
        respuestas_mensajes.append(f"Creado hasta: {creado_hasta}")
    if descripcion != "":
        descripcion = safe_string(descripcion, save_enie=True)
        if descripcion != "":
            consulta = consulta.filter(OfiDocumento.descripcion.contains(descripcion))
            respuestas_mensajes.append(f"Descripción: {descripcion}")
    if estado != "":
        estado = safe_string(estado)
        if estado in OfiDocumento.ESTADOS:
            consulta = consulta.filter(OfiDocumento.estado == estado)
            respuestas_mensajes.append(f"Estado: {estado}")
        else:
            return CustomPage(success=False, message="No es válido el estado")
    if folio != "":
        folio = safe_string(folio)
        if folio != "":
            consulta = consulta.filter(OfiDocumento.folio.contains(folio))
            respuestas_mensajes.append(f"Folio: {folio}")
    if numero is not None:
        consulta = consulta.filter(OfiDocumento.folio_num == numero)
        respuestas_mensajes.append(f"Folio número: {numero}")
    if usuario_email != "":
        try:
            usuario_email = safe_email(usuario_email, search_fragment=True)
        except ValueError:
            return CustomPage(success=False, message="El usuario_email no es válido")
        consulta = consulta.filter(Usuario.email.contains(usuario_email))
        respuestas_mensajes.append(f"Usuario email: {usuario_email}")
    consulta = consulta.filter(OfiDocumento.estatus == "A")
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
    return paginate(consulta.order_by(OfiDocumento.creado.desc()))
