"""
Usuarios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_email, safe_string
from ..models.autoridades import Autoridad
from ..models.permisos import Permiso
from ..models.usuarios import Usuario
from ..schemas.usuarios import OneUsuarioOut, UsuarioOut

usuarios = APIRouter(prefix="/api/v5/usuarios", tags=["usuarios"])


@usuarios.get("/{email}", response_model=OneUsuarioOut)
async def detalle_usuario(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    email: str,
):
    """Detalle de una usuarios a partir de su e-mail"""
    if current_user.permissions.get("USUARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        email = str(safe_email(email))
    except ValueError:
        return OneUsuarioOut(success=False, message="No es válido el email")
    try:
        usuario = database.query(Usuario).filter_by(email=email).one()
    except (MultipleResultsFound, NoResultFound):
        return OneUsuarioOut(success=False, message="No existe ese usuario")
    if usuario.estatus != "A":
        return OneUsuarioOut(success=False, message="No está habilitado ese usuario")
    return OneUsuarioOut(success=True, message=f"Detalle de {email}", data=UsuarioOut.model_validate(usuario))


@usuarios.get("", response_model=CustomPage[UsuarioOut])
async def paginado_usuarios(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    apellido_paterno: str = "",
    apellido_materno: str = "",
    autoridad_clave: str = "",
    email: str = "",
    nombres: str = "",
):
    """Paginado de usuarios"""
    if current_user.permissions.get("USUARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(Usuario)
    if apellido_paterno != "":
        apellido_paterno = safe_string(apellido_paterno, save_enie=True)
        if apellido_paterno != "":
            consulta = consulta.filter(Usuario.apellido_paterno.contains(apellido_paterno))
    if apellido_materno != "":
        apellido_materno = safe_string(apellido_materno, save_enie=True)
        if apellido_materno != "":
            consulta = consulta.filter(Usuario.apellido_materno.contains(apellido_materno))
    if autoridad_clave != "":
        try:
            autoridad_clave = safe_clave(autoridad_clave)
        except ValueError:
            return CustomPage(success=False, message="No es válida la clave de la autoridad")
        try:
            autoridad = database.query(Autoridad).filter(Autoridad.clave == autoridad_clave).one()
        except (MultipleResultsFound, NoResultFound):
            return CustomPage(success=False, message="No existe esa autoridad")
        if autoridad.estatus != "A":
            return CustomPage(success=False, message="No está habilitada esa autoridad")
        consulta = consulta.join(Autoridad).filter(Autoridad.clave == autoridad_clave)
    if email != "":
        try:
            email = str(safe_email(email, search_fragment=True))
        except ValueError:
            return CustomPage(success=False, message="No es válido el email")
        consulta = consulta.filter(Usuario.email.contains(email))
    if nombres != "":
        nombres = safe_string(nombres, save_enie=True)
        if nombres != "":
            consulta = consulta.filter(Usuario.nombres.contains(nombres))
    return paginate(consulta.filter(Usuario.estatus == "A").order_by(Usuario.email))
