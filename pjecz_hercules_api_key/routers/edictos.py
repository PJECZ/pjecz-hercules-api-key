"""
Edictos
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
from ..dependencies.safe_string import safe_clave
from ..models.autoridades import Autoridad
from ..models.bitacoras_apis import BitacoraAPI
from ..models.edictos import Edicto
from ..models.permisos import Permiso
from ..schemas.edictos import EdictoOut, EdictoRAGOut, OneEdictoOut

PREFIX = "/api/v5/edictos"
edictos = APIRouter(prefix=PREFIX, tags=["edictos"])


@edictos.get("/{edicto_id}", response_model=OneEdictoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    edicto_id: int,
):
    """Detalle de un edicto a partir de su ID"""
    if current_user.permissions.get("EDICTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    edicto = database.query(Edicto).get(edicto_id)
    if edicto is None:
        return OneEdictoOut(success=False, message="No existe ese edicto")
    if edicto.estatus != "A":
        return OneEdictoOut(success=False, message="No es activa ese edicto, está eliminado")
    return OneEdictoOut(success=True, message="Detalle de un edicto", data=EdictoRAGOut.model_validate(edicto))


@edictos.get("", response_model=CustomPage[EdictoOut])
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
):
    """Paginado de edictos"""
    if current_user.permissions.get("EDICTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Edicto)
    if autoridad_clave != "":
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
    if creado is not None:
        consulta = consulta.filter(Edicto.creado.cast(Date) == creado)
    if creado_desde is not None:
        consulta = consulta.filter(Edicto.creado.cast(Date) >= creado_desde)
    if creado_hasta is not None:
        consulta = consulta.filter(Edicto.creado.cast(Date) <= creado_hasta)
    if fecha is not None:
        consulta = consulta.filter(Edicto.fecha == fecha)
    else:
        if fecha_desde is not None:
            consulta = consulta.filter(Edicto.fecha >= fecha_desde)
        if fecha_hasta is not None:
            consulta = consulta.filter(Edicto.fecha <= fecha_hasta)
    bitacora_api = BitacoraAPI(
        usuario_id=current_user.id,
        api_nombre=settings.API_NOMBRE,
        api_ruta=PREFIX,
        peticion="GET",
    )
    database.add(bitacora_api)
    database.commit()
    return paginate(consulta.filter(Edicto.estatus == "A").order_by(Edicto.id.desc()))
