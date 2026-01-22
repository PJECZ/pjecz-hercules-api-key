"""
Exh Exhortos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..config.settings import Settings, get_settings
from ..dependencies.authentications import UsuarioInDB, get_current_active_user
from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave, safe_string, safe_url
from ..models.autoridades import Autoridad
from ..models.estados import Estado
from ..models.exh_areas import ExhArea
from ..models.exh_exhortos import ExhExhorto
from ..models.exh_exhortos_archivos import ExhExhortoArchivo
from ..models.exh_exhortos_partes import ExhExhortoParte
from ..models.exh_tipos_diligencias import ExhTipoDiligencia
from ..models.materias import Materia
from ..models.municipios import Municipio
from ..models.permisos import Permiso
from ..schemas.exh_exhortos import ExhExhortoIn, ExhExhortoOut, ExhExhortoPaginadoOut, OneExhExhortoOut
from ..schemas.exh_exhortos_archivos import ExhExhortoArchivoOut
from ..schemas.exh_exhortos_partes import ExhExhortoParteOut

exh_exhortos = APIRouter(prefix="/api/v5/exh_exhortos", tags=["exhortos"])


@exh_exhortos.get("/{exh_exhorto_id}", response_model=OneExhExhortoOut)
async def detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    exh_exhorto_id: int,
):
    """Detalle de un exhorto a partir de su ID"""
    if current_user.permissions.get("EXH EXHORTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Consultar el exhorto
    exh_exhorto = database.query(ExhExhorto).get(exh_exhorto_id)
    if exh_exhorto is None:
        return OneExhExhortoOut(success=False, message="No existe ese exhorto")
    if exh_exhorto.estatus != "A":
        return OneExhExhortoOut(success=False, message="No es activo ese exhorto, está eliminado")

    # Consultar las partes activas (estatus == "A")
    partes = []
    for parte in exh_exhorto.exh_exhortos_partes:
        if parte.estatus == "A":
            partes.append(ExhExhortoParteOut.model_validate(parte))
    exh_exhorto.exh_exhorto_partes = partes

    # Consultar los archivos activos (estaus == "A")
    archivos = []
    for archivo in exh_exhorto.exh_exhortos_archivos:
        if archivo.estatus == "A":
            archivos.append(ExhExhortoArchivoOut.model_validate(archivo))
    exh_exhorto.exh_exhorto_archivos = archivos

    # Entregar
    return OneExhExhortoOut(
        success=True,
        message="Detalle del exhorto",
        data=ExhExhortoOut.model_validate(exh_exhorto),
    )


@exh_exhortos.get("", response_model=CustomPage[ExhExhortoPaginadoOut])
async def paginado(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    autoridad_clave: str = "",
):
    """Paginado de exh_exhortos"""
    if current_user.permissions.get("EXH EXHORTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    consulta = database.query(ExhExhorto)
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
    return paginate(consulta.filter(ExhExhorto.estatus == "A").order_by(ExhExhorto.id.desc()))


@exh_exhortos.post("", response_model=OneExhExhortoOut)
async def crear(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    database: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    exh_exhorto_in: ExhExhortoIn,
):
    """Crear un exhorto"""
    if current_user.permissions.get("EXH EXHORTOS", 0) < Permiso.CREAR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Validar la autoridad
    try:
        exh_exhorto_in.autoridad_clave = safe_clave(exh_exhorto_in.autoridad_clave)
    except ValueError:
        return OneExhExhortoOut(success=False, message="No es válida la clave de la autoridad")
    autoridad = database.query(Autoridad).filter(Autoridad.clave == exh_exhorto_in.autoridad_clave).first()
    if autoridad is None:
        return OneExhExhortoOut(success=False, message="No existe esa autoridad")
    if autoridad.estatus != "A":
        return OneExhExhortoOut(success=False, message="Esa autoridad no está activa")

    # Validar el área
    try:
        exh_exhorto_in.exh_area_clave = safe_clave(exh_exhorto_in.exh_area_clave)
    except ValueError:
        return OneExhExhortoOut(success=False, message="No es válida la clave del área")
    exh_area = database.query(ExhArea).filter(ExhArea.clave == exh_exhorto_in.exh_area_clave).first()
    if exh_area is None:
        return OneExhExhortoOut(success=False, message="No existe ese área")
    if exh_area.estatus != "A":
        return OneExhExhortoOut(success=False, message="Ese área no está activa")

    # Consultar el estado configurado
    estado = database.query(Estado).filter(Estado.clave == str(settings.ESTADO_CLAVE).zfill(2)).first()
    if estado is None:
        return OneExhExhortoOut(success=False, message="No existe el estado configurado o falta la clave INEGI")

    # Validar el juzgado_origen_id
    try:
        juzgado_origen_clave = safe_clave(exh_exhorto_in.juzgado_origen_id)
    except ValueError:
        return OneExhExhortoOut(success=False, message="No es válida la clave del juzgado_origen_id")
    juzgado_origen = database.query(Autoridad).filter(Autoridad.clave == juzgado_origen_clave).first()
    if juzgado_origen is None:
        return OneExhExhortoOut(success=False, message="No existe ese juzgado_origen")
    if juzgado_origen.estatus != "A":
        return OneExhExhortoOut(success=False, message="Ese juzgado_origen no está activo")

    # Validar la materia
    try:
        exh_exhorto_in.materia_clave = safe_clave(exh_exhorto_in.materia_clave)
    except ValueError:
        return OneExhExhortoOut(success=False, message="No es válida la clave de la materia")
    materia = database.query(Materia).filter(Materia.clave == exh_exhorto_in.materia_clave).first()
    if materia is None:
        return OneExhExhortoOut(success=False, message="No existe esa materia")
    if materia.estatus != "A":
        return OneExhExhortoOut(success=False, message="Esa materia no está activa")

    # Consultar el tipo de diligencia con clave "OTR" (OTROS)
    exh_tipo_diligencia = database.query(ExhTipoDiligencia).filter(ExhTipoDiligencia.clave == "OTR").first()
    if exh_tipo_diligencia is None:
        return OneExhExhortoOut(success=False, message='No existe el tipo de diligencia con clave "OTR"')
    if exh_tipo_diligencia.estatus != "A":
        return OneExhExhortoOut(success=False, message='El tipo de diligencia con clave "OTR" no está activo')

    # Validar número de fojas
    if exh_exhorto_in.fojas <= 0:
        return OneExhExhortoOut(success=False, message="El número de fojas no es válido, debe ser mayor a 0")

    # Validar número de días de respuesta
    if exh_exhorto_in.dias_responder < 0:
        return OneExhExhortoOut(success=False, message="El número de días de respuesta no es válido, debe ser mayor 0")

    # Validar las Partes
    partes = []  # Vamos a ir guardando las partes válidas
    for exh_exhorto_parte_in in exh_exhorto_in.exh_exhorto_partes:
        parte = {}
        # Validar nombre de la parte
        parte_nombre = safe_string(exh_exhorto_parte_in.nombre)
        if parte_nombre == "":
            return OneExhExhortoOut(success=False, message="El nombre de una parte no es válido")
        parte["nombre"] = parte_nombre
        # Validar el tipo de parte
        if exh_exhorto_parte_in.tipo_parte not in ExhExhortoParte.TIPOS_PARTES:
            return OneExhExhortoOut(success=False, message="El tipo de parte de una parte no es válido")
        parte["tipo_parte"] = exh_exhorto_parte_in.tipo_parte
        # Validar si es persona moral, sí o no
        parte["es_persona_moral"] = exh_exhorto_parte_in.es_persona_moral
        if exh_exhorto_parte_in.es_persona_moral == False:
            # Validar el apellido paterno de la parte
            parte_apellido_paterno = safe_string(exh_exhorto_parte_in.apellido_paterno)
            if parte_apellido_paterno == "":
                return OneExhExhortoOut(
                    success=False, message="El apellido paterno de una persona física no es válido o está vacío"
                )
            parte["apellido_paterno"] = parte_apellido_paterno
            # Validar el apellido materno de la parte
            parte_apellido_materno = safe_string(exh_exhorto_parte_in.apellido_materno)
            if parte_apellido_materno == "":
                return OneExhExhortoOut(
                    success=False, message="El apellido materno de una persona física no es válido o está vacío"
                )
            parte["apellido_materno"] = parte_apellido_materno
            # Validar el género de la parte
            if exh_exhorto_parte_in.genero not in ExhExhortoParte.GENEROS:
                return OneExhExhortoOut(success=False, message="El género de una parte no es válido")
            parte["genero"] = exh_exhorto_parte_in.genero
        else:
            parte["apellido_paterno"] = ""
            parte["apellido_materno"] = ""
            parte["genero"] = "-"  # Como es persona moral, se pone el guion
        # Validar el tipo de parte nombre
        parte["tipo_parte_nombre"] = ""
        if exh_exhorto_parte_in.tipo_parte_nombre == 0:
            parte_nombre_parte = safe_string(exh_exhorto_parte_in.tipo_parte_nombre)
            if parte_nombre_parte == "":
                return OneExhExhortoOut(success=False, message="El nombre de una parte no es válido y es necesario")
            parte["tipo_parte_nombre"] = parte_nombre_parte
        # Añadir parte al listado de partes
        partes.append(parte)

    # Validar Archivos
    archivos = []  # Vamos a ir guardando los archivos validados
    for exh_exhorto_archivo_in in exh_exhorto_in.exh_exhorto_archivos:
        archivo = {}
        # Validar nombre del archivo
        nombre_archivo = safe_string(exh_exhorto_archivo_in.nombre_archivo)
        if nombre_archivo == "":
            return OneExhExhortoOut(success=False, message="El nombre de un archivo no es válido")
        archivo["nombre_archivo"] = nombre_archivo
        # Validar el tipo de documento del archivo
        if exh_exhorto_archivo_in.tipo_documento not in ExhExhortoArchivo.TIPOS_DOCUMENTOS:
            return OneExhExhortoOut(success=False, message="El tipo de documento de un archivo no es válido")
        archivo["tipo_documento"] = exh_exhorto_archivo_in.tipo_documento
        # Validar la url del archivo
        url = safe_url(exh_exhorto_archivo_in.url)
        if url == "":
            return OneExhExhortoOut(success=False, message="La URL de un archivo no es válida")
        archivo["url"] = url
        # Validar tamaño del archivo
        tamanio = exh_exhorto_archivo_in.tamano
        if tamanio is None:
            archivo["tamano"] = None
        else:
            if tamanio < 0:
                return OneExhExhortoOut(success=False, message="El tamaño de un archivo no es válido")
            archivo["tamano"] = tamanio
        # Añadir archivo al listado de archivos
        archivos.append(archivo)

    # Insertar el exhorto
    exh_exhorto = ExhExhorto(
        autoridad_id=autoridad.id,
        exh_area_id=exh_area.id,
        exh_tipo_diligencia_id=exh_tipo_diligencia.id,
        municipio_origen_id=juzgado_origen.municipio.id,
        exhorto_origen_id=exh_exhorto_in.exhorto_origen_id,
        municipio_destino_id=autoridad.municipio.id,
        materia_clave=materia.clave,
        materia_nombre=materia.nombre,
        juzgado_origen_id=juzgado_origen.clave,
        juzgado_origen_nombre=juzgado_origen.descripcion,
        numero_expediente_origen=exh_exhorto_in.numero_expediente_origen,
        tipo_juicio_asunto_delitos=exh_exhorto_in.tipo_juicio_asunto_delitos,
        fojas=exh_exhorto_in.fojas,
        dias_responder=exh_exhorto_in.dias_responder,
        remitente="INTERNO",
        estado="PENDIENTE",
    )
    database.add(exh_exhorto)

    # Insertar las Partes
    for parte in partes:
        exh_exhorto_parte = ExhExhortoParte(
            exh_exhorto=exh_exhorto,
            nombre=parte["nombre"],
            apellido_paterno=parte["apellido_paterno"],
            apellido_materno=parte["apellido_materno"],
            genero=parte["genero"],
            es_persona_moral=parte["es_persona_moral"],
            tipo_parte=parte["tipo_parte"],
            tipo_parte_nombre=parte["tipo_parte_nombre"],
        )
        database.add(exh_exhorto_parte)

    # Insertar los Archivos
    for archivo in archivos:
        exh_exhorto_archivo = ExhExhortoArchivo(
            exh_exhorto=exh_exhorto,
            nombre_archivo=archivo["nombre_archivo"],
            tipo_documento=archivo["tipo_documento"],
            url=archivo["url"],
            tamano=archivo["tamano"],
            estado="RECIBIDO",
        )
        database.add(exh_exhorto_archivo)

    # Hacer el commit para cerrar la transacción
    database.commit()

    # Refrescar el exhorto
    database.refresh(exh_exhorto)

    # Consultar las partes activas (estatus == "B") aunque se supone que todas lo están
    partes = []
    for parte in exh_exhorto.exh_exhortos_partes:
        if parte.estatus == "A":
            partes.append(ExhExhortoParteOut.model_validate(parte))
    exh_exhorto.exh_exhorto_partes = partes

    # Consultar los archivos activos (estaus == "A") aunque se supone que todas lo están
    archivos = []
    for archivo in exh_exhorto.exh_exhortos_archivos:
        if archivo.estatus == "A":
            archivos.append(ExhExhortoArchivoOut.model_validate(archivo))
    exh_exhorto.exh_exhorto_archivos = archivos

    # Entregar
    return OneExhExhortoOut(
        success=True,
        message="Exhorto creado",
        data=ExhExhortoOut.model_validate(exh_exhorto),
    )
