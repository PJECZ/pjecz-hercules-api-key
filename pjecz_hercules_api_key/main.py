"""
PJECZ Hércules API Key
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from pjecz_hercules_api_key.config.settings import get_settings
from pjecz_hercules_api_key.routers.arc_documentos import arc_documentos
from pjecz_hercules_api_key.routers.arc_documentos_tipos import arc_documentos_tipos
from pjecz_hercules_api_key.routers.arc_juzgados_extintos import arc_juzgados_extintos
from pjecz_hercules_api_key.routers.arc_remesas import arc_remesas
from pjecz_hercules_api_key.routers.arc_remesas_documentos import arc_remesas_documentos
from pjecz_hercules_api_key.routers.autoridades import autoridades
from pjecz_hercules_api_key.routers.bitacoras_apis import bitacoras_apis
from pjecz_hercules_api_key.routers.distritos import distritos
from pjecz_hercules_api_key.routers.domicilios import domicilios
from pjecz_hercules_api_key.routers.edictos import edictos
from pjecz_hercules_api_key.routers.estados import estados
from pjecz_hercules_api_key.routers.exh_exhortos import exh_exhortos
from pjecz_hercules_api_key.routers.funcionarios import funcionarios
from pjecz_hercules_api_key.routers.funcionarios_oficinas import funcionarios_oficinas
from pjecz_hercules_api_key.routers.listas_de_acuerdos import listas_de_acuerdos
from pjecz_hercules_api_key.routers.materias import materias
from pjecz_hercules_api_key.routers.materias_tipos_juicios import materias_tipos_juicios
from pjecz_hercules_api_key.routers.modulos import modulos
from pjecz_hercules_api_key.routers.municipios import municipios
from pjecz_hercules_api_key.routers.ofi_documentos import ofi_documentos
from pjecz_hercules_api_key.routers.ofi_documentos_adjuntos import ofi_documentos_adjuntos
from pjecz_hercules_api_key.routers.ofi_documentos_destinatarios import ofi_documentos_destinatarios
from pjecz_hercules_api_key.routers.oficinas import oficinas
from pjecz_hercules_api_key.routers.permisos import permisos
from pjecz_hercules_api_key.routers.redams import redams
from pjecz_hercules_api_key.routers.roles import roles
from pjecz_hercules_api_key.routers.sentencias import sentencias
from pjecz_hercules_api_key.routers.soportes_categorias import soportes_categorias
from pjecz_hercules_api_key.routers.soportes_tickets import soportes_tickets
from pjecz_hercules_api_key.routers.usuarios import usuarios
from pjecz_hercules_api_key.routers.usuarios_roles import usuarios_roles
from pjecz_hercules_api_key.routers.vsp_digitalizaciones import vsp_digitalizaciones

# FastAPI
app = FastAPI(
    title="PJECZ API key de Plataforma Web",
    description="API de uso público para consultar edictos, listas de acuerdos, sentencias, etc.",
    docs_url="/docs",
    redoc_url=None,
)

# CORSMiddleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS.split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rutas
app.include_router(arc_documentos)
app.include_router(arc_documentos_tipos)
app.include_router(arc_juzgados_extintos)
app.include_router(arc_remesas)
app.include_router(arc_remesas_documentos)
app.include_router(autoridades)
app.include_router(bitacoras_apis)
app.include_router(distritos)
app.include_router(domicilios)
app.include_router(edictos)
app.include_router(estados)
app.include_router(exh_exhortos)
app.include_router(funcionarios)
app.include_router(funcionarios_oficinas)
app.include_router(listas_de_acuerdos)
app.include_router(materias)
app.include_router(materias_tipos_juicios)
app.include_router(modulos)
app.include_router(municipios)
app.include_router(ofi_documentos)
app.include_router(ofi_documentos_adjuntos)
app.include_router(ofi_documentos_destinatarios)
app.include_router(oficinas)
app.include_router(permisos)
app.include_router(redams)
app.include_router(roles)
app.include_router(sentencias)
app.include_router(soportes_categorias)
app.include_router(soportes_tickets)
app.include_router(usuarios)
app.include_router(usuarios_roles)
app.include_router(vsp_digitalizaciones)

# Paginación
add_pagination(app)


# Mensaje de Bienvenida
@app.get("/")
async def root():
    """Mensaje de Bienvenida"""
    return {"message": "API del Poder Judicial del Estado de Coahuila de Zaragoza. Solicitudes a informatica en pjecz.gob.mx."}
