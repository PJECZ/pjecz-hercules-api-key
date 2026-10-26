"""
Archivos Documentos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_expediente, safe_string
from pjecz_hercules_api_key.models.arc_documentos import ArcDocumento
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.arc_documentos import ArcDocumentoOut

arc_documentos = APIRouter(prefix="/arc_documentos")


@arc_documentos.get("", response_model=CustomPage[ArcDocumentoOut])
def arc_documentos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    actor: Annotated[str | None, Query()] = None,
    anio: Annotated[int | None, Query(ge=1900, le=2100)] = None,
    autoridad_clave: Annotated[str | None, Query()] = None,
    demandado: Annotated[str | None, Query()] = None,
    expediente: Annotated[str | None, Query()] = None,
    expediente_numero: Annotated[int | None, Query(ge=1)] = None,
    ubicacion: Annotated[str | None, Query()] = None,
):
    """Archivos Documentos paginado"""
    if current_user.permissions.get("ARC DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ArcDocumento).where(ArcDocumento.estatus == "A")
    if actor and (actor := safe_string(actor)):
        stmt = stmt.where(ArcDocumento.actor.ilike(f"%{actor}%"))
    if anio is not None:
        stmt = stmt.where(ArcDocumento.anio == anio)
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(ArcDocumento.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if demandado and (demandado := safe_string(demandado)):
        stmt = stmt.where(ArcDocumento.demandado.ilike(f"%{demandado}%"))
    if expediente and (expediente := safe_expediente(expediente)):
        stmt = stmt.where(ArcDocumento.expediente == expediente)
    if expediente_numero is not None:
        stmt = stmt.where(ArcDocumento.expediente_numero == expediente_numero)
    if ubicacion and (ubicacion := safe_string(ubicacion)):
        if ubicacion not in ArcDocumento.UBICACIONES:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="La ubicación no es válida")
        stmt = stmt.where(ArcDocumento.ubicacion == ubicacion)
    stmt = stmt.order_by(ArcDocumento.id.desc())
    return paginate(session, stmt)
