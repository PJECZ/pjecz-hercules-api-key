"""
Sentencias
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Date
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from pjecz_hercules_api_key.config.settings import Settings, get_settings
from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.dependencies.safe_string import safe_clave, safe_string
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.bitacoras_apis import BitacoraAPI
from pjecz_hercules_api_key.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.sentencias import Sentencia
from pjecz_hercules_api_key.schemas.sentencias import OneSentenciaOut, SentenciaOut, SentenciaRAGOut

PREFIX = "/api/v5/sentencias"
sentencias = APIRouter(prefix=PREFIX, tags=["sentencias"])


@sentencias.get("/{sentencia_id}", response_model=OneSentenciaOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    sentencia_id: int,
):
    """Detalle de una sentencia a partir de su ID"""
    if current_user.permissions.get("SENTENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    sentencia = database.query(Sentencia).get(sentencia_id)
    if sentencia is None:
        return OneSentenciaOut(success=False, message="No existe esa sentencia")
    if sentencia.estatus != "A":
        return OneSentenciaOut(success=False, message="No es activa esa sentencia, está eliminada")
    return OneSentenciaOut(success=True, message="Detalle de una sentencia", data=SentenciaRAGOut.model_validate(sentencia))


@sentencias.get("", response_model=CustomPage[SentenciaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    autoridad_clave: str = "",
    creado: date | None = None,
    creado_desde: date | None = None,
    creado_hasta: date | None = None,
    fecha: date | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    materia_tipo_juicio_id: int | None = None,
):
    """Paginado de sentencias"""
    if current_user.permissions.get("SENTENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    respuestas_mensajes = []
    consulta = database.query(Sentencia)
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
        consulta = consulta.filter(Sentencia.creado.cast(Date) == creado)
        respuestas_mensajes.append(f"Creado: {creado}")
    if creado_desde is not None:
        consulta = consulta.filter(Sentencia.creado.cast(Date) >= creado_desde)
        respuestas_mensajes.append(f"Creado desde: {creado_desde}")
    if creado_hasta is not None:
        consulta = consulta.filter(Sentencia.creado.cast(Date) <= creado_hasta)
        respuestas_mensajes.append(f"Creado hasta: {creado_hasta}")
    if fecha is not None:
        consulta = consulta.filter(Sentencia.fecha == fecha)
        respuestas_mensajes.append(f"Fecha: {fecha}")
    else:
        if fecha_desde is not None:
            consulta = consulta.filter(Sentencia.fecha >= fecha_desde)
            respuestas_mensajes.append(f"Fecha desde: {fecha_desde}")
        if fecha_hasta is not None:
            consulta = consulta.filter(Sentencia.fecha <= fecha_hasta)
            respuestas_mensajes.append(f"Fecha hasta: {fecha_hasta}")
    if materia_tipo_juicio_id is not None:
        try:
            materia_tipo_juicio = database.query(MateriaTipoJuicio).filter(MateriaTipoJuicio.id == materia_tipo_juicio_id).one()
        except MultipleResultsFound, NoResultFound:
            return CustomPage(success=False, message="No existe ese tipo de juicio para materia")
        if materia_tipo_juicio.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese tipo de juicio para materia")
        consulta = (
            consulta.join(MateriaTipoJuicio)
            .filter(MateriaTipoJuicio.id == materia_tipo_juicio_id)
            .filter(MateriaTipoJuicio.estatus == "A")
        )
        respuestas_mensajes.append(f"Tipo de juicio: {materia_tipo_juicio_id}")
    consulta = consulta.filter(Sentencia.estatus == "A")
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
    return paginate(consulta.order_by(Sentencia.id.desc()))
