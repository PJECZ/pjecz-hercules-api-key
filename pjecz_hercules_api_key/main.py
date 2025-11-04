"""
PJECZ Hércules API Key
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from .config.settings import get_settings
from .routers.autoridades import autoridades
from .routers.distritos import distritos
from .routers.domicilios import domicilios
from .routers.edictos import edictos
from .routers.estados import estados
from .routers.exh_exhortos import exh_exhortos
from .routers.funcionarios import funcionarios
from .routers.listas_de_acuerdos import listas_de_acuerdos
from .routers.materias import materias
from .routers.materias_tipos_juicios import materias_tipos_juicios
from .routers.modulos import modulos
from .routers.municipios import municipios
from .routers.oficinas import oficinas
from .routers.permisos import permisos
from .routers.roles import roles
from .routers.sentencias import sentencias
from .routers.soportes_categorias import soportes_categorias
from .routers.soportes_tickets import soportes_tickets
from .routers.usuarios import usuarios
from .routers.usuarios_roles import usuarios_roles

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
app.include_router(autoridades)
app.include_router(distritos)
app.include_router(domicilios)
app.include_router(edictos)
app.include_router(estados)
app.include_router(exh_exhortos)
app.include_router(funcionarios)
app.include_router(listas_de_acuerdos)
app.include_router(materias)
app.include_router(materias_tipos_juicios)
app.include_router(modulos)
app.include_router(municipios)
app.include_router(oficinas)
app.include_router(permisos)
app.include_router(roles)
app.include_router(sentencias)
app.include_router(soportes_categorias)
app.include_router(soportes_tickets)
app.include_router(usuarios)
app.include_router(usuarios_roles)

# Paginación
add_pagination(app)


# Mensaje de Bienvenida
@app.get("/")
async def root():
    """Mensaje de Bienvenida"""
    return {"message": "API del Poder Judicial del Estado de Coahuila de Zaragoza. Solicitudes a informatica en pjecz.gob.mx."}
