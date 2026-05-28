"""
VASPEC Digitalizaciones, rutas
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Date
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..config.settings import Settings, get_settings
from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_string
from ..models.autoridades import Autoridad
from ..models.bitacoras_apis import BitacoraAPI
from ..models.permisos import Permiso
from ..models.vsp_digitalizaciones import VspDigitalizacion
from ..schemas.vsp_digitalizaciones import VspDigitalizacionOut

PREFIX = "/api/v5/vsp_digitalizaciones"
vsp_digitalizaciones = APIRouter(prefix=PREFIX, tags=["vsp digitalizaciones"])


@vsp_digitalizaciones.get("", response_model=CustomPage[VspDigitalizacionOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    autoridad_clave: str = "",
    creado: date | None = None,
    creado_desde: date | None = None,
    creado_hasta: date | None = None,
    expediente_anio: int | None = None,
    expediente_num: int | None = None,
):
    """Paginado de digitalizaciones"""
    if current_user.permissions.get("VSP DIGITALIZACIONES", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(VspDigitalizacion)
    if autoridad_clave != "":
        try:
            autoridad_clave = safe_clave(autoridad_clave)
        except ValueError:
            return CustomPage(success=False, message="No es válida la clave de la autoridad")
        try:
            autoridad = database.query(Autoridad).filter(Autoridad.clave == autoridad_clave).one()
        except MultipleResultsFound, NoResultFound:
            return CustomPage(success=False, message="No existe esa autoridad")
        if autoridad.estatus != "A":
            return CustomPage(success=False, message="No está habilitada esa autoridad")
        consulta = consulta.join(Autoridad).filter(Autoridad.clave == autoridad_clave)
        respuestas_mensajes.append(f"Autoridad: {autoridad_clave}")
    if creado is not None:
        consulta = consulta.filter(VspDigitalizacion.creado.cast(Date) == creado)
        respuestas_mensajes.append(f"Creado: {creado}")
    if creado_desde is not None:
        consulta = consulta.filter(VspDigitalizacion.creado.cast(Date) >= creado_desde)
        respuestas_mensajes.append(f"Creado desde: {creado_desde}")
    if creado_hasta is not None:
        consulta = consulta.filter(VspDigitalizacion.creado.cast(Date) <= creado_hasta)
        respuestas_mensajes.append(f"Creado hasta: {creado_hasta}")
    if expediente_anio is not None:
        consulta = consulta.filter(VspDigitalizacion.expediente_anio == expediente_anio)
        respuestas_mensajes.append(f"Expediente año: {expediente_anio}")
    if expediente_num is not None:
        consulta = consulta.filter(VspDigitalizacion.expediente_num == expediente_num)
        respuestas_mensajes.append(f"Expediente número: {expediente_num}")
    consulta = consulta.filter(VspDigitalizacion.estatus == "A")
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
    return paginate(
        consulta.order_by(VspDigitalizacion.expediente_anio, VspDigitalizacion.expediente_num, VspDigitalizacion.descripcion)
    )
