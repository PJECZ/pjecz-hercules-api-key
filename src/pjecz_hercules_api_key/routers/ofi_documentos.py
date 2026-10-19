"""
Oficios Documentos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_email, safe_string
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
        stmt = stmt.where(Usuario.email.ilike(f"%{usuario_email}%"))
    if descripcion and (descripcion := safe_string(descripcion)):
        stmt = stmt.where(OfiDocumento.descripcion.ilike(f"%{descripcion}%"))
    stmt = stmt.order_by(OfiDocumento.creado.desc())
    return paginate(session, stmt)
