"""
Listas de Acuerdos
"""

from datetime import date
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.config.setttings import get_settings
from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.google_cloud_storage import get_blob_name_from_url, get_file_from_gcs
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_string, validate_fechas
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.listas_de_acuerdos import ListaDeAcuerdo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.listas_de_acuerdos import ListaDeAcuerdoOut, OneListaDeAcuerdoOut

listas_de_acuerdos = APIRouter(prefix="/listas_de_acuerdos")


@listas_de_acuerdos.get("", response_model=CustomPage[ListaDeAcuerdoOut])
def listas_de_acuerdos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
    distrito_clave: Annotated[str | None, Query()] = None,
    fecha: Annotated[date | None, Query()] = None,
    fecha_desde: Annotated[date | None, Query()] = None,
    fecha_hasta: Annotated[date | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
):
    """Listas de Acuerdos paginado"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    validate_fechas(fecha, fecha_desde, fecha_hasta)
    stmt = select(ListaDeAcuerdo).where(ListaDeAcuerdo.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(ListaDeAcuerdo.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        if not autoridad_clave:
            stmt = stmt.join(ListaDeAcuerdo.autoridad)
        stmt = stmt.join(Autoridad.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    if fecha is not None:
        stmt = stmt.where(ListaDeAcuerdo.fecha == fecha)
    if fecha_desde is not None:
        stmt = stmt.where(ListaDeAcuerdo.fecha >= fecha_desde)
    if fecha_hasta is not None:
        stmt = stmt.where(ListaDeAcuerdo.fecha <= fecha_hasta)
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(ListaDeAcuerdo.descripcion.ilike(f"%{descripcion}%"))
    stmt = stmt.order_by(ListaDeAcuerdo.id.desc())
    return paginate(session, stmt)


@listas_de_acuerdos.get("/visualizar/{id}", response_class=StreamingResponse)
def listas_de_acuerdos_visualizar(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    id: int,
):
    """Visualizar el archivo PDF de una Lista de Acuerdos"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    lista_de_acuerdo = session.get(ListaDeAcuerdo, id)
    if lista_de_acuerdo is None or lista_de_acuerdo.estatus != "A":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if lista_de_acuerdo.url.strip() == "":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File URL is empty")
    bucket_name = get_settings().GCP_BUCKET_LISTAS_DE_ACUERDOS
    blob_name = get_blob_name_from_url(bucket_name, lista_de_acuerdo.url)
    contenido = get_file_from_gcs(bucket_name, blob_name)
    nombre = f"lista-de-acuerdos-{lista_de_acuerdo.autoridad.clave}-{lista_de_acuerdo.fecha.isoformat()}.pdf"
    return StreamingResponse(
        BytesIO(contenido),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nombre}"'},
    )


@listas_de_acuerdos.get("/{id}", response_model=OneListaDeAcuerdoOut)
def listas_de_acuerdos_detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    id: int,
):
    """Detalle de una Lista de Acuerdos"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    lista_de_acuerdo = session.get(ListaDeAcuerdo, id)
    if lista_de_acuerdo is None or lista_de_acuerdo.estatus != "A":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return OneListaDeAcuerdoOut(success=True, message="Success", data=ListaDeAcuerdoOut.model_validate(lista_de_acuerdo))
