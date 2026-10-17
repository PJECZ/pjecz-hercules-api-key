"""
Main
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from pjecz_hercules_api_key.routers.autoridades import autoridades
from pjecz_hercules_api_key.routers.distritos import distritos
from pjecz_hercules_api_key.routers.domicilios import domicilios
from pjecz_hercules_api_key.routers.edictos import edictos
from pjecz_hercules_api_key.routers.glosas import glosas
from pjecz_hercules_api_key.routers.listas_de_acuerdos import listas_de_acuerdos
from pjecz_hercules_api_key.routers.materias import materias
from pjecz_hercules_api_key.routers.materias_tipos_juicios import materias_tipos_juicios
from pjecz_hercules_api_key.routers.modulos import modulos
from pjecz_hercules_api_key.routers.oficinas import oficinas
from pjecz_hercules_api_key.routers.permisos import permisos
from pjecz_hercules_api_key.routers.roles import roles
from pjecz_hercules_api_key.routers.sentencias import sentencias
from pjecz_hercules_api_key.routers.usuarios import usuarios
from pjecz_hercules_api_key.routers.usuarios_roles import usuarios_roles

app = FastAPI(root_path="/api/v5")

# Configurar CORS para permitir peticiones del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar routers
app.include_router(autoridades)
app.include_router(distritos)
app.include_router(domicilios)
app.include_router(edictos)
app.include_router(glosas)
app.include_router(listas_de_acuerdos)
app.include_router(materias)
app.include_router(materias_tipos_juicios)
app.include_router(modulos)
app.include_router(oficinas)
app.include_router(permisos)
app.include_router(roles)
app.include_router(sentencias)
app.include_router(usuarios)
app.include_router(usuarios_roles)

# Pagination
add_pagination(app)
