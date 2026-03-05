"""
Arc Documentos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..config.settings import Settings, get_settings
from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_string
from ..models.arc_documentos import ArcDocumento
from ..models.autoridades import Autoridad
from ..models.bitacoras_apis import BitacoraAPI
from ..models.permisos import Permiso
from ..schemas.arc_documentos import ArcDocumentoOut

PREFIX = "/api/v5/arc_documentos"
arc_documentos = APIRouter(prefix=PREFIX, tags=["archivos"])


@arc_documentos.get("", response_model=CustomPage[ArcDocumentoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    actor: str = "",
    anio: int | None = None,
    autoridad_clave: str = "",
    demandado: str = "",
    expediente: str = "",
    expediente_numero: int | None = None,
    ubicacion: str = "",
):
    """Paginado de documentos"""
    if current_user.permissions.get("ARC DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(ArcDocumento)
    if actor != "":
        actor = safe_string(actor, save_enie=True)
        if actor != "":
            consulta = consulta.filter(ArcDocumento.actor.contains(actor))
            respuestas_mensajes.append(f"Actor: {actor}")
    if anio is not None:
        consulta = consulta.filter(ArcDocumento.anio == anio)
        respuestas_mensajes.append(f"Año: {anio}")
    if autoridad_clave != "":
        try:
            autoridad_clave = safe_clave(autoridad_clave)
        except ValueError:
            return CustomPage(success=False, message="La autoridad_clave no es válida")
        consulta = consulta.join(Autoridad).filter(Autoridad.clave.contains(autoridad_clave))
        respuestas_mensajes.append(f"Autoridad: {autoridad_clave}")
    if demandado != "":
        demandado = safe_string(demandado, save_enie=True)
        if demandado != "":
            consulta = consulta.filter(ArcDocumento.demandado.contains(demandado))
            respuestas_mensajes.append(f"Demandado: {demandado}")
    if expediente != "":
        expediente = safe_string(expediente)
        if expediente != "":
            consulta = consulta.filter(ArcDocumento.expediente.contains(expediente))
            respuestas_mensajes.append(f"Expediente: {expediente}")
    if expediente_numero is not None:
        consulta = consulta.filter(ArcDocumento.expediente_numero == expediente_numero)
        respuestas_mensajes.append(f"Expediente número: {expediente_numero}")
    if ubicacion != "":
        ubicacion = safe_string(ubicacion)
        if ubicacion in ArcDocumento.UBICACIONES:
            consulta = consulta.filter(ArcDocumento.ubicacion == ubicacion)
            respuestas_mensajes.append(f"Ubicación: {ubicacion}")
        else:
            return CustomPage(success=False, message="No es válida la ubicación")
    consulta = consulta.filter(ArcDocumento.estatus == "A")
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
    return paginate(consulta.order_by(ArcDocumento.id.desc()))
