"""
Arc Juzgados Extintos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.models.arc_juzgados_extintos import ArcJuzgadoExtinto
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas.arc_juzgados_extintos import ArcJuzgadoExtintoOut

arc_juzgados_extintos = APIRouter(prefix="/api/v5/arc_juzgados_extintos", tags=["archivos"])


@arc_juzgados_extintos.get("", response_model=CustomPage[ArcJuzgadoExtintoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de juzgados extintos"""
    if current_user.permissions.get("ARC JUZGADOS EXTINTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(ArcJuzgadoExtinto)
    return paginate(consulta.filter(ArcJuzgadoExtinto.estatus == "A").order_by(ArcJuzgadoExtinto.clave))
