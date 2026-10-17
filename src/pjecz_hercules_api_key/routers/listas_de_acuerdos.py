"""
Listas de Acuerdos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.listas_de_acuerdos import ListaDeAcuerdo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.listas_de_acuerdos import ListaDeAcuerdoOut

listas_de_acuerdos = APIRouter(prefix="/listas_de_acuerdos")


@listas_de_acuerdos.get("", response_model=CustomPage[ListaDeAcuerdoOut])
def listas_de_acuerdos_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Listas de Acuerdos paginado"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ListaDeAcuerdo).where(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.id.desc())
    return paginate(session, stmt)
