"""
Glosas
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
from pjecz_hercules_api_key.core.validation import safe_clave, safe_expediente, safe_string, validate_fechas
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.glosas import Glosa
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.glosas import GlosaOut, OneGlosaOut

glosas = APIRouter(prefix="/glosas")


@glosas.get("", response_model=CustomPage[GlosaOut])
def glosas_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
    distrito_clave: Annotated[str | None, Query()] = None,
    fecha: Annotated[date | None, Query()] = None,
    fecha_desde: Annotated[date | None, Query()] = None,
    fecha_hasta: Annotated[date | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
    expediente: Annotated[str | None, Query()] = None,
):
    """Glosas paginado"""
    if current_user.permissions.get("GLOSAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    validate_fechas(fecha, fecha_desde, fecha_hasta)
    stmt = select(Glosa).where(Glosa.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(Glosa.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        if not autoridad_clave:
            stmt = stmt.join(Glosa.autoridad)
        stmt = stmt.join(Autoridad.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    if fecha is not None:
        stmt = stmt.where(Glosa.fecha == fecha)
    if fecha_desde is not None:
        stmt = stmt.where(Glosa.fecha >= fecha_desde)
    if fecha_hasta is not None:
        stmt = stmt.where(Glosa.fecha <= fecha_hasta)
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(Glosa.descripcion.ilike(f"%{descripcion}%"))
    if expediente and (expediente := safe_expediente(expediente)):
        stmt = stmt.where(Glosa.expediente == expediente)
    stmt = stmt.order_by(Glosa.id.desc())
    return paginate(session, stmt)


@glosas.get("/visualizar/{id}", response_class=StreamingResponse)
def glosas_visualizar(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    id: int,
):
    """Visualizar el archivo PDF de una Glosa"""
    if current_user.permissions.get("GLOSAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    glosa = session.get(Glosa, id)
    if glosa is None or glosa.estatus != "A":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if glosa.url.strip() == "":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File URL is empty")
    bucket_name = get_settings().GCP_BUCKET_GLOSAS
    blob_name = get_blob_name_from_url(bucket_name, glosa.url)
    contenido = get_file_from_gcs(bucket_name, blob_name)
    nombre = f"glosa-{glosa.autoridad.clave}-{glosa.fecha.isoformat()}.pdf"
    return StreamingResponse(
        BytesIO(contenido),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nombre}"'},
    )


@glosas.get("/{id}", response_model=OneGlosaOut)
def glosas_detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    id: int,
):
    """Detalle de una Glosa"""
    if current_user.permissions.get("GLOSAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    glosa = session.get(Glosa, id)
    if glosa is None or glosa.estatus != "A":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return OneGlosaOut(success=True, message="Success", data=GlosaOut.model_validate(glosa))
