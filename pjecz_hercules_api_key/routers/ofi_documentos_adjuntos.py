"""
Oficios Documentos Adjuntos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_string, safe_uuid
from ..models.ofi_documentos import OfiDocumento
from ..models.ofi_documentos_adjuntos import OfiDocumentoAdjunto
from ..models.permisos import Permiso
from ..schemas.ofi_documentos_adjuntos import OfiDocumentoAdjuntoOut, OneOfiDocumentoAdjuntoOut

ofi_documentos_adjuntos = APIRouter(prefix="/api/v5/ofi_documentos_adjuntos", tags=["oficios"])


@ofi_documentos_adjuntos.get("/{ofi_documento_adjunto_id}", response_model=OneOfiDocumentoAdjuntoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    ofi_documento_adjunto_id: str,
):
    """Detalle de un adjunto a partir de su ID"""
    if current_user.permissions.get("OFI DOCUMENTOS ADJUNTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        ofi_documento_adjunto_uuid = safe_uuid(ofi_documento_adjunto_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la UUID")
    ofi_documento_adjunto = database.query(OfiDocumentoAdjunto).get(ofi_documento_adjunto_uuid)
    if not ofi_documento_adjunto:
        return OneOfiDocumentoAdjuntoOut(success=False, message="No existe ese adjunto")
    if ofi_documento_adjunto.estatus != "A":
        return OneOfiDocumentoAdjuntoOut(success=False, message="No está habilitado ese adjunto")
    return OneOfiDocumentoAdjuntoOut(
        success=True,
        message="Detalle de un adjunto",
        data=OfiDocumentoAdjuntoOut.model_validate(ofi_documento_adjunto),
    )


@ofi_documentos_adjuntos.get("", response_model=CustomPage[OfiDocumentoAdjuntoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    descripcion: str = "",
    ofi_documento_id: str = "",
):
    """Paginado de adjuntos"""
    if current_user.permissions.get("OFI DOCUMENTOS ADJUNTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(OfiDocumentoAdjunto)
    if descripcion != "":
        descripcion = safe_string(descripcion)
        if descripcion != "":
            consulta = consulta.filter(OfiDocumentoAdjunto.descripcion.contains(descripcion))
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
        consulta = consulta.filter(OfiDocumentoAdjunto.ofi_documento_id == ofi_documento_uuid)
    return paginate(consulta.filter(OfiDocumentoAdjunto.estatus == "A").order_by(OfiDocumentoAdjunto.creado.desc()))
