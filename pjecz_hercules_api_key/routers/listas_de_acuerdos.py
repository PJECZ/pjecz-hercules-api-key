"""
Listas de Acuerdos
"""

from datetime import date
from io import BytesIO
from typing import Annotated
from urllib.parse import unquote, urlparse

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi_pagination.ext.sqlalchemy import paginate
from google.cloud import storage
from sqlalchemy import Date
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..config.settings import Settings, get_settings
from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.autoridades import Autoridad
from ..models.bitacoras_apis import BitacoraAPI
from ..models.listas_de_acuerdos import ListaDeAcuerdo
from ..models.permisos import Permiso
from ..schemas.listas_de_acuerdos import ListaDeAcuerdoOut, ListaDeAcuerdoRAGOut, OneListaDeAcuerdoOut

PREFIX = "/api/v5/listas_de_acuerdos"
listas_de_acuerdos = APIRouter(prefix=PREFIX, tags=["listas de acuerdos"])


@listas_de_acuerdos.get("/visualizar/{lista_de_acuerdo_id}")
async def visualizar(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    lista_de_acuerdo_id: int,
):
    """Visualizar el archivo de una lista de acuerdos en un iframe a partir de su ID"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    lista_de_acuerdo = database.query(ListaDeAcuerdo).get(lista_de_acuerdo_id)
    if lista_de_acuerdo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe esa lista de acuerdos")
    if lista_de_acuerdo.estatus != "A":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No es activa esa lista de acuerdos, está eliminada")

    # Validar que la URL del archivo esté definida
    if lista_de_acuerdo.url is None or lista_de_acuerdo.url.strip() == "":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No está definida la URL del archivo")

    # Definir el blob_name a partir de lista_de_acuerdo.url, porque este contiene la ruta completa
    url_descompuesto = urlparse(lista_de_acuerdo.url)
    url_sin_dominio = url_descompuesto.path[1:]
    blob_name = unquote("/".join(url_sin_dominio.split("/")[1:]))

    # Obtener el archivo desde Google Cloud Storage
    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(settings.GCP_BUCKET_LISTAS_DE_ACUERDOS)
        blob = bucket.get_blob(blob_name)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo accesar al depósito de archivos: {error}",
        )

    # Validar que el blob existe
    if blob is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el archivo {blob_name} en el depósito {settings.GCP_BUCKET_LISTAS_DE_ACUERDOS}",
        )

    # Descargar el archivo en memoria
    archivo_contenido = BytesIO()
    try:
        archivo_contenido.write(blob.download_as_bytes())
        archivo_contenido.seek(0)  # Volver al inicio del archivo
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo descargar el archivo desde el depósito: {error}",
        )

    # Definir el nombre del archivo para la respuesta
    autoridad_clave = lista_de_acuerdo.autoridad.clave
    fecha_str = lista_de_acuerdo.fecha.strftime("%Y-%m-%d")
    archivo_nombre = f"lista_de_acuerdos_{autoridad_clave}_{fecha_str}.pdf"

    # Entregar el archivo
    return StreamingResponse(
        content=archivo_contenido,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={archivo_nombre}"},
    )


@listas_de_acuerdos.get("/{lista_de_acuerdo_id}", response_model=OneListaDeAcuerdoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    lista_de_acuerdo_id: int,
):
    """Detalle de una lista de acuerdos a partir de su ID"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    lista_de_acuerdo = database.query(ListaDeAcuerdo).get(lista_de_acuerdo_id)
    if lista_de_acuerdo is None:
        return OneListaDeAcuerdoOut(success=False, message="No existe esa lista de acuerdos")
    if lista_de_acuerdo.estatus != "A":
        return OneListaDeAcuerdoOut(success=False, message="No es activa esa lista de acuerdos, está eliminada")
    return OneListaDeAcuerdoOut(
        success=True, message="Detalle de una lista de acuerdos", data=ListaDeAcuerdoRAGOut.model_validate(lista_de_acuerdo)
    )


@listas_de_acuerdos.get("", response_model=CustomPage[ListaDeAcuerdoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    autoridad_clave: str = "",
    creado: date | None = None,
    creado_desde: date | None = None,
    creado_hasta: date | None = None,
    fecha: date | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
):
    """Paginado de listas_de_acuerdos"""
    if current_user.permissions.get("LISTAS DE ACUERDOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(ListaDeAcuerdo)
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
    if creado is not None:
        consulta = consulta.filter(ListaDeAcuerdo.creado.cast(Date) == creado)
    if creado_desde is not None:
        consulta = consulta.filter(ListaDeAcuerdo.creado.cast(Date) >= creado_desde)
    if creado_hasta is not None:
        consulta = consulta.filter(ListaDeAcuerdo.creado.cast(Date) <= creado_hasta)
    if fecha is not None:
        consulta = consulta.filter(ListaDeAcuerdo.fecha == fecha)
    else:
        if fecha_desde is not None:
            consulta = consulta.filter(ListaDeAcuerdo.fecha >= fecha_desde)
        if fecha_hasta is not None:
            consulta = consulta.filter(ListaDeAcuerdo.fecha <= fecha_hasta)
    bitacora_api = BitacoraAPI(
        usuario_id=current_user.id,
        api_nombre=settings.API_NOMBRE,
        api_ruta=PREFIX,
        peticion="GET",
    )
    database.add(bitacora_api)
    database.commit()
    return paginate(consulta.filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.id.desc()))
