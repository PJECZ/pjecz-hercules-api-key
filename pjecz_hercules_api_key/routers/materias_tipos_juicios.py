"""
Materias Tipos de Juicios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from pjecz_hercules_api_key.dependencies.authentications import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.dependencies.database import Session, get_db
from pjecz_hercules_api_key.dependencies.fastapi_pagination_custom_page import CustomPage
from pjecz_hercules_api_key.dependencies.safe_string import safe_clave
from pjecz_hercules_api_key.schemas.materias_tipos_juicios import MateriaTipoJuicioOut

from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.schemas
materias_tipos_juicios = APIRouter(prefix="/api/v5/materias_tipos_juicios", tags=["materias"])


@materias_tipos_juicios.get("", response_model=CustomPage[MateriaTipoJuicioOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    materia_clave: str = "",
):
    """Paginado de materias_tipos_juicios"""
    if current_user.permissions.get("MATERIAS TIPOS JUICIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(MateriaTipoJuicio)
    if materia_clave != "":
        try:
            materia_clave = safe_clave(materia_clave)
        except ValueError:
            return CustomPage(success=False, message="No es válida la clave de la materia")
        try:
            materia = database.query(Materia).filter(Materia.clave == materia_clave).one()
        except MultipleResultsFound, NoResultFound:
            return CustomPage(success=False, message="No existe esa materia")
        if materia.estatus != "A":
            return CustomPage(success=False, message="No está habilitada esa materia")
        consulta = consulta.join(Materia).filter(Materia.clave == materia_clave)
    return paginate(consulta.filter(MateriaTipoJuicio.estatus == "A").order_by(MateriaTipoJuicio.descripcion))
