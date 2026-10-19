"""
Soportes Categorias
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_string
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.soportes_categorias import SoporteCategoria
from pjecz_hercules_api_key.schemas.soportes_categorias import SoporteCategoriaOut

soportes_categorias = APIRouter(prefix="/soportes_categorias")


@soportes_categorias.get("", response_model=CustomPage[SoporteCategoriaOut])
def soportes_categorias_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    nombre: Annotated[str | None, Query()] = None,
):
    """Soportes Categorias paginado"""
    if current_user.permissions.get("SOPORTES CATEGORIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(SoporteCategoria).where(SoporteCategoria.estatus == "A")
    if nombre and (nombre := safe_string(nombre)):
        stmt = stmt.where(SoporteCategoria.nombre.ilike(f"%{nombre}%"))
    stmt = stmt.order_by(SoporteCategoria.nombre)
    return paginate(session, stmt)
