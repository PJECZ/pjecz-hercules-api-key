"""
Main
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from pjecz_hercules_api_key.routers.autoridades import autoridades
from pjecz_hercules_api_key.routers.distritos import distritos
from pjecz_hercules_api_key.routers.materias import materias

app = FastAPI()

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
app.include_router(materias)

# Pagination
add_pagination(app)


@app.get("/api/saludo")
def dar_saludo():
    return {"message": "Hola mundo!"}
