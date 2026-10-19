"""
Usuarios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from pjecz_hercules_api_key.core.authentication import UsuarioInDB, get_current_active_user
from pjecz_hercules_api_key.core.database import Session, get_session
from pjecz_hercules_api_key.core.pagination import CustomPage
from pjecz_hercules_api_key.core.validation import safe_clave, safe_curp, safe_email, safe_string
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.oficinas import Oficina
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.schemas.usuarios import UsuarioOut

usuarios = APIRouter(prefix="/usuarios")


@usuarios.get("", response_model=CustomPage[UsuarioOut])
def usuarios_paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    autoridad_clave: Annotated[str | None, Query()] = None,
    distrito_clave: Annotated[str | None, Query()] = None,
    curp: Annotated[str | None, Query()] = None,
    email: Annotated[str | None, Query()] = None,
    oficina_clave: Annotated[str | None, Query()] = None,
    nombres: Annotated[str | None, Query()] = None,
    apellido_paterno: Annotated[str | None, Query()] = None,
    apellido_materno: Annotated[str | None, Query()] = None,
):
    """Usuarios paginado"""
    if current_user.permissions.get("USUARIOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    stmt = select(Usuario).where(Usuario.estatus == "A")
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        stmt = stmt.join(Usuario.autoridad).where(Autoridad.clave.ilike(f"%{autoridad_clave}%"))
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        if not autoridad_clave:
            stmt = stmt.join(Usuario.autoridad)
        stmt = stmt.join(Autoridad.distrito).where(Distrito.clave.ilike(f"%{distrito_clave}%"))
    if curp and (curp := safe_curp(curp)):
        stmt = stmt.where(Usuario.curp == curp)
    if email and (email := safe_email(email)):
        stmt = stmt.where(Usuario.email == email)
    if oficina_clave and (oficina_clave := safe_clave(oficina_clave, 32)):
        stmt = stmt.join(Usuario.oficina).where(Oficina.clave.ilike(f"%{oficina_clave}%"))
    if nombres and (nombres := safe_string(nombres)):
        stmt = stmt.where(Usuario.nombres.ilike(f"%{nombres}%"))
    if apellido_paterno and (apellido_paterno := safe_string(apellido_paterno)):
        stmt = stmt.where(Usuario.apellido_paterno.ilike(f"%{apellido_paterno}%"))
    if apellido_materno and (apellido_materno := safe_string(apellido_materno)):
        stmt = stmt.where(Usuario.apellido_materno.ilike(f"%{apellido_materno}%"))
    stmt = stmt.order_by(Usuario.email)
    return paginate(session, stmt)
