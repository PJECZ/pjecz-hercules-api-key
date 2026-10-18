"""
Main
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from pjecz_hercules_api_key.routers.arc_documentos import arc_documentos
from pjecz_hercules_api_key.routers.arc_documentos_tipos import arc_documentos_tipos
from pjecz_hercules_api_key.routers.arc_juzgados_extintos import arc_juzgados_extintos
from pjecz_hercules_api_key.routers.arc_remesas import arc_remesas
from pjecz_hercules_api_key.routers.arc_remesas_documentos import arc_remesas_documentos
from pjecz_hercules_api_key.routers.autoridades import autoridades
from pjecz_hercules_api_key.routers.distritos import distritos
from pjecz_hercules_api_key.routers.domicilios import domicilios
from pjecz_hercules_api_key.routers.edictos import edictos
from pjecz_hercules_api_key.routers.estados import estados
from pjecz_hercules_api_key.routers.exh_exhortos import exh_exhortos
from pjecz_hercules_api_key.routers.exh_exhortos_archivos import exh_exhortos_archivos
from pjecz_hercules_api_key.routers.exh_exhortos_partes import exh_exhortos_partes
from pjecz_hercules_api_key.routers.funcionarios import funcionarios
from pjecz_hercules_api_key.routers.funcionarios_oficinas import funcionarios_oficinas
from pjecz_hercules_api_key.routers.glosas import glosas
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
from pjecz_hercules_api_key.routers.repsvm_agresores import repsvm_agresores
from pjecz_hercules_api_key.routers.roles import roles
from pjecz_hercules_api_key.routers.sentencias import sentencias
from pjecz_hercules_api_key.routers.soportes_categorias import soportes_categorias
from pjecz_hercules_api_key.routers.soportes_tickets import soportes_tickets
from pjecz_hercules_api_key.routers.usuarios import usuarios
from pjecz_hercules_api_key.routers.usuarios_roles import usuarios_roles

app = FastAPI(root_path="/api/v5")

# Configurar CORS para permitir peticiones del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Agregar routers
app.include_router(arc_documentos)
app.include_router(arc_documentos_tipos)
app.include_router(arc_juzgados_extintos)
app.include_router(arc_remesas)
app.include_router(arc_remesas_documentos)
app.include_router(autoridades)
app.include_router(distritos)
app.include_router(domicilios)
app.include_router(edictos)
app.include_router(estados)
app.include_router(exh_exhortos)
app.include_router(exh_exhortos_archivos)
app.include_router(exh_exhortos_partes)
app.include_router(funcionarios)
app.include_router(funcionarios_oficinas)
app.include_router(glosas)
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
app.include_router(repsvm_agresores)
app.include_router(roles)
app.include_router(sentencias)
app.include_router(soportes_categorias)
app.include_router(soportes_tickets)
app.include_router(usuarios)
app.include_router(usuarios_roles)

# Pagination
add_pagination(app)
