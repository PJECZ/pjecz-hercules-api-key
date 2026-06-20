"""
Exh Exhortos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.dependencies.safe_string import safe_clave, safe_string, safe_url
from pjecz_hercules_api_key.schemas.exh_exhortos import ExhExhortoIn, ExhExhortoOut, ExhExhortoPaginadoOut, OneExhExhortoOut
from pjecz_hercules_api_key.schemas.exh_exhortos_archivos import ExhExhortoArchivoOut
from pjecz_hercules_api_key.schemas.exh_exhortos_partes import ExhExhortoParteOut

from pjecz_hercules_api_key.config.settings import Settings, get_settings
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.estados import Estado
from pjecz_hercules_api_key.models.exh_areas import ExhArea
from pjecz_hercules_api_key.models.exh_exhortos import ExhExhorto
from pjecz_hercules_api_key.models.exh_exhortos_archivos import ExhExhortoArchivo
from pjecz_hercules_api_key.models.exh_exhortos_partes import ExhExhortoParte
from pjecz_hercules_api_key.models.exh_tipos_diligencias import ExhTipoDiligencia
from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.models.municipios import Municipio
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemasfrom pjecz_hercules_api_key.schemasfrom pjecz_hercules_api_key.schemas
exh_exhortos = APIRouter(prefix="/api/v5/exh_exhortos", tags=["exhortos"])


@exh_exhortos.get("/{exh_exhorto_id}", response_model=OneExhExhortoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    exh_exhorto_id: int,
):
    """Detalle de un exhorto a partir de su ID"""
    if current_user.permissions.get("EXH EXHORTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Consultar el exhorto
    exh_exhorto = database.query(ExhExhorto).get(exh_exhorto_id)
    if exh_exhorto is None:
        return OneExhExhortoOut(success=False, message="No existe ese exhorto")
    if exh_exhorto.estatus != "A":
        return OneExhExhortoOut(success=False, message="No es activo ese exhorto, está eliminado")

    # Consultar las partes activas (estatus == "A")
    partes = []
    for parte in exh_exhorto.exh_exhortos_partes:
        if parte.estatus == "A":
            partes.append(ExhExhortoParteOut.model_validate(parte))
    exh_exhorto.exh_exhorto_partes = partes

    # Consultar los archivos activos (estaus == "A")
    archivos = []
    for archivo in exh_exhorto.exh_exhortos_archivos:
        if archivo.estatus == "A":
            archivos.append(ExhExhortoArchivoOut.model_validate(archivo))
    exh_exhorto.exh_exhorto_archivos = archivos

    # Entregar
    return OneExhExhortoOut(
        success=True,
        message="Detalle del exhorto",
        data=ExhExhortoOut.model_validate(exh_exhorto),
    )


@exh_exhortos.get("", response_model=CustomPage[ExhExhortoPaginadoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    autoridad_clave: str = "",
):
    """Paginado de exh_exhortos"""
    if current_user.permissions.get("EXH EXHORTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(ExhExhorto)
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
    return paginate(consulta.filter(ExhExhorto.estatus == "A").order_by(ExhExhorto.id.desc()))
