"""
Oficios Documentos
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_email, safe_string, validate_fechas
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.ofi_documentos import OfiDocumento
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.schemas.ofi_documentos import OfiDocumentoOut

ofi_documentos = APIRouter(prefix="/ofi_documentos")


@ofi_documentos.get("", response_model=CustomPage[OfiDocumentoOut])
def ofi_documentos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    usuario_autoridad_clave: Annotated[str | None, Query()] = None,
    usuario_email: Annotated[str | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
):
    """Oficios Documentos paginado"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(OfiDocumento).where(OfiDocumento.estatus == "A")
    if usuario_autoridad_clave and (usuario_autoridad_clave := safe_clave(usuario_autoridad_clave)):
        stmt = (
            stmt.join(OfiDocumento.usuario).join(Usuario.autoridad).where(Autoridad.clave.ilike(f"%{usuario_autoridad_clave}%"))
        )
    if usuario_email and (usuario_email := safe_email(usuario_email)):
        if not usuario_autoridad_clave:
            stmt = stmt.join(OfiDocumento.usuario)
        stmt = stmt.where(Usuario.email == usuario_email)
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(OfiDocumento.descripcion.ilike(f"%{descripcion}%"))
    stmt = stmt.order_by(OfiDocumento.creado.desc())
    return paginate(session, stmt)


@ofi_documentos.get("/mis_oficios", response_model=CustomPage[OfiDocumentoOut])
def ofi_documentos_mis_oficios(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    anio: Annotated[int | None, Query(ge=1900, le=2100)] = None,
    creado: Annotated[date | None, Query()] = None,
    creado_desde: Annotated[date | None, Query()] = None,
    creado_hasta: Annotated[date | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
    estado: Annotated[str | None, Query()] = None,
    folio: Annotated[str | None, Query()] = None,
    numero: Annotated[int | None, Query(ge=1)] = None,
):
    """Oficios Documentos de Mis Oficios paginado"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    validate_fechas(creado, creado_desde, creado_hasta)
    stmt = select(OfiDocumento).where(OfiDocumento.estatus == "A").where(OfiDocumento.usuario_id == current_user.id)
    if anio is not None:
        stmt = stmt.where(OfiDocumento.folio_anio == anio)
    if creado is not None:
        stmt = stmt.where(func.date(OfiDocumento.creado) == creado)
    if creado_desde is not None:
        stmt = stmt.where(func.date(OfiDocumento.creado) >= creado_desde)
    if creado_hasta is not None:
        stmt = stmt.where(func.date(OfiDocumento.creado) <= creado_hasta)
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(OfiDocumento.descripcion.ilike(f"%{descripcion}%"))
    if estado and (estado := safe_string(estado)):
        if estado not in OfiDocumento.ESTADOS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="El estado no es válido")
        stmt = stmt.where(OfiDocumento.estado == estado)
    if folio and (folio := safe_string(folio)):
        stmt = stmt.where(OfiDocumento.folio.ilike(f"%{folio}%"))
    if numero is not None:
        stmt = stmt.where(OfiDocumento.folio_num == numero)
    stmt = stmt.order_by(OfiDocumento.creado.desc())
    return paginate(session, stmt)


@ofi_documentos.get("/mi_autoridad", response_model=CustomPage[OfiDocumentoOut])
def ofi_documentos_mi_autoridad(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    anio: Annotated[int | None, Query(ge=1900, le=2100)] = None,
    creado: Annotated[date | None, Query()] = None,
    creado_desde: Annotated[date | None, Query()] = None,
    creado_hasta: Annotated[date | None, Query()] = None,
    descripcion: Annotated[str | None, Query()] = None,
    estado: Annotated[str | None, Query()] = None,
    folio: Annotated[str | None, Query()] = None,
    numero: Annotated[int | None, Query(ge=1)] = None,
    usuario_email: Annotated[str | None, Query()] = None,
):
    """Oficios Documentos de Mi Autoridad paginado"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    validate_fechas(creado, creado_desde, creado_hasta)
    stmt = (
        select(OfiDocumento)
        .join(OfiDocumento.usuario)
        .join(Usuario.autoridad)
        .where(OfiDocumento.estatus == "A")
        .where(Usuario.autoridad_id == current_user.autoridad_id)
    )
    if anio is not None:
        stmt = stmt.where(OfiDocumento.folio_anio == anio)
    if creado is not None:
        stmt = stmt.where(func.date(OfiDocumento.creado) == creado)
    if creado_desde is not None:
        stmt = stmt.where(func.date(OfiDocumento.creado) >= creado_desde)
    if creado_hasta is not None:
        stmt = stmt.where(func.date(OfiDocumento.creado) <= creado_hasta)
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(OfiDocumento.descripcion.ilike(f"%{descripcion}%"))
    if estado and (estado := safe_string(estado)):
        if estado not in OfiDocumento.ESTADOS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="El estado no es válido")
        stmt = stmt.where(OfiDocumento.estado == estado)
    if folio and (folio := safe_string(folio)):
        stmt = stmt.where(OfiDocumento.folio.ilike(f"%{folio}%"))
    if numero is not None:
        stmt = stmt.where(OfiDocumento.folio_num == numero)
    if usuario_email and (usuario_email := safe_email(usuario_email)):
        stmt = stmt.where(Usuario.email == usuario_email)
    stmt = stmt.order_by(OfiDocumento.creado.desc())
    return paginate(session, stmt)
