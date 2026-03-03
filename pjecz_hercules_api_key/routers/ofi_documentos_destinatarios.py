"""
Oficios Documentos Destinatarios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_email, safe_uuid
from ..models.ofi_documentos import OfiDocumento
from ..models.ofi_documentos_destinatarios import OfiDocumentoDestinatario
from ..models.permisos import Permiso
from ..models.usuarios import Usuario
from ..schemas.ofi_documentos_destinatarios import OfiDocumentoDestinatarioOut

ofi_documentos_destinatarios = APIRouter(prefix="/api/v5/ofi_documentos_destinatarios", tags=["oficios"])


@ofi_documentos_destinatarios.get("", response_model=CustomPage[OfiDocumentoDestinatarioOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    ofi_documento_id: str = "",
    usuario_email: str = "",
):
    """Paginado de destinatarios"""
    if current_user.permissions.get("OFI DOCUMENTOS DESTINATARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(OfiDocumentoDestinatario)
    if ofi_documento_id != "":
        try:
            ofi_documento_uuid = safe_uuid(ofi_documento_id)
        except ValueError:
            return CustomPage(success=False, message="No es válida la UUID")
        ofi_documento = database.query(OfiDocumento).get(ofi_documento_uuid)
        if not ofi_documento:
            return CustomPage(success=False, message="No existe ese documento")
        if ofi_documento.estatus != "A":
            return CustomPage(success=False, message="No está habilitado ese documento")
        consulta = consulta.filter(OfiDocumentoDestinatario.ofi_documento_id == ofi_documento_uuid)
    if usuario_email != "":
        try:
            usuario_email = safe_email(usuario_email, search_fragment=True)
        except ValueError:
            return CustomPage(success=False, message="El usuario_email no es válido")
        consulta = consulta.join(Usuario).filter(Usuario.email.contains(usuario_email))
    return paginate(consulta.filter(OfiDocumentoDestinatario.estatus == "A").order_by(OfiDocumentoDestinatario.creado.desc()))
