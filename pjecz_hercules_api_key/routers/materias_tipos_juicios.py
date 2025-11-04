"""
Materias Tipos de Juicios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.materias import Materia
from ..models.materias_tipos_juicios import MateriaTipoJuicio
from ..models.permisos import Permiso
from ..schemas.materias_tipos_juicios import MateriaTipoJuicioOut

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
    if materia_clave:
        try:
            materia_clave = safe_clave(materia_clave)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
        consulta = consulta.join(Materia).filter(Materia.clave == materia_clave).filter(Materia.estatus == "A")
    return paginate(consulta.filter(MateriaTipoJuicio.estatus == "A").order_by(MateriaTipoJuicio.descripcion))
