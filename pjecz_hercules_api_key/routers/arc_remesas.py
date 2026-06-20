"""
Arc Remesas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.schemas.arc_remesas import ArcRemesaOut

from pjecz_hercules_api_key.models.arc_remesas import ArcRemesa
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas
arc_remesas = APIRouter(prefix="/api/v5/arc_remesas", tags=["archivos"])


@arc_remesas.get("", response_model=CustomPage[ArcRemesaOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de remesas"""
    if current_user.permissions.get("ARC REMESAS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(ArcRemesa)
    return paginate(consulta.filter(ArcRemesa.estatus == "A").order_by(ArcRemesa.id.desc()))
