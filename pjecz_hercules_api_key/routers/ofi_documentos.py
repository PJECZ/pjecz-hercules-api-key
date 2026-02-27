"""
Oficios Documentos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_email, safe_string, safe_uuid
from ..models.ofi_documentos import OfiDocumento
from ..models.permisos import Permiso
from ..models.usuarios import Usuario
from ..schemas.ofi_documentos import OfiDocumentoOut, OneOfiDocumentoOut

ofi_documentos = APIRouter(prefix="/api/v5/ofi_documentos", tags=["oficios"])


@ofi_documentos.get("/{ofi_documento_id}", response_model=OneOfiDocumentoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    ofi_documento_id: str,
):
    """Detalle de un documento a partir de su ID"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        ofi_documento_uuid = safe_uuid(ofi_documento_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la UUID")
    ofi_documento = database.query(OfiDocumento).get(ofi_documento_uuid)
    if not ofi_documento:
        return OneOfiDocumentoOut(success=False, message="No existe ese documento")
    if ofi_documento.estatus != "A":
        return OneOfiDocumentoOut(success=False, message="No está habilitado ese documento")
    return OneOfiDocumentoOut(
        success=True,
        message="Detalle de un documento",
        data=OfiDocumentoOut.model_validate(ofi_documento),
    )


@ofi_documentos.get("", response_model=CustomPage[OfiDocumentoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    anio: int | None = None,
    descripcion: str = "",
    estado: str = "",
    folio: str = "",
    numero: int | None = None,
    usuario_email: str = "",
):
    """Paginado de documentos"""
    if current_user.permissions.get("OFI DOCUMENTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(OfiDocumento)
    if anio is not None:
        consulta = consulta.filter(OfiDocumento.folio_anio == anio)
    if descripcion != "":
        descripcion = safe_string(descripcion)
        if descripcion != "":
            consulta = consulta.filter(OfiDocumento.descripcion.contains(descripcion))
    if estado != "":
        estado = safe_string(estado)
        if estado in OfiDocumento.ESTADOS:
            consulta = consulta.filter(OfiDocumento.estado == estado)
        else:
            return CustomPage(success=False, message="No es válido el estado")
    if folio != "":
        folio = safe_string(folio)
        if folio != "":
            consulta = consulta.filter(OfiDocumento.folio.contains(folio))
    if numero is not None:
        consulta = consulta.filter(OfiDocumento.folio_num == numero)
    if usuario_email != "":
        try:
            usuario_email = safe_email(usuario_email, search_fragment=True)
        except ValueError:
            return CustomPage(success=False, message="El usuario_email no es válido")
        consulta = consulta.join(Usuario).filter(Usuario.email.contains(usuario_email))
    return paginate(consulta.filter(OfiDocumento.estatus == "A").order_by(OfiDocumento.creado.desc()))
