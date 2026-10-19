"""
Oficios Documentos Destinatarios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_email
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.ofi_documentos_destinatarios import OfiDocumentoDestinatario
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.schemas.ofi_documentos_destinatarios import OfiDocumentoDestinatarioOut

ofi_documentos_destinatarios = APIRouter(prefix="/ofi_documentos_destinatarios")


@ofi_documentos_destinatarios.get("", response_model=CustomPage[OfiDocumentoDestinatarioOut])
def ofi_documentos_destinatarios_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    usuario_autoridad_clave: Annotated[str | None, Query()] = None,
    usuario_email: Annotated[str | None, Query()] = None,
):
    """Oficios Documentos Destinatarios paginado"""
    if current_user.permissions.get("OFI DOCUMENTOS DESTINATARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(OfiDocumentoDestinatario).where(OfiDocumentoDestinatario.estatus == "A")
    if usuario_autoridad_clave and (usuario_autoridad_clave := safe_clave(usuario_autoridad_clave)):
        stmt = (
            stmt.join(OfiDocumentoDestinatario.usuario)
            .join(Usuario.autoridad)
            .where(Autoridad.clave.ilike(f"%{usuario_autoridad_clave}%"))
        )
    if usuario_email and (usuario_email := safe_email(usuario_email)):
        if not usuario_autoridad_clave:
            stmt = stmt.join(OfiDocumentoDestinatario.usuario)
        stmt = stmt.where(Usuario.email.ilike(f"%{usuario_email}%"))
    stmt = stmt.order_by(OfiDocumentoDestinatario.creado.desc())
    return paginate(session, stmt)
