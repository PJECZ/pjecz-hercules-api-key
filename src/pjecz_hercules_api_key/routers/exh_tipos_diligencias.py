"""
EXH Tipos Diligencias
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.models.exh_tipos_diligencias import ExhTipoDiligencia
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.exh_tipos_diligencias import ExhTipoDiligenciaOut

exh_tipos_diligencias = APIRouter(prefix="/exh_tipos_diligencias")


@exh_tipos_diligencias.get("", response_model=CustomPage[ExhTipoDiligenciaOut])
def exh_tipos_diligencias_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """EXH Tipos Diligencias paginado"""
    if current_user.permissions.get("EXH TIPOS DILIGENCIAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(ExhTipoDiligencia).where(ExhTipoDiligencia.estatus == "A").order_by(ExhTipoDiligencia.clave)
    return paginate(session, stmt)
