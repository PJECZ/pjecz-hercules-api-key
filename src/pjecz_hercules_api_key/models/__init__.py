"""
Models

Importa todos los modelos para que SQLAlchemy pueda resolver las relaciones declaradas con nombres de clase.
"""

from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.edictos import Edicto
from pjecz_hercules_api_key.models.glosas import Glosa
from pjecz_hercules_api_key.models.listas_de_acuerdos import ListaDeAcuerdo
from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_api_key.models.modulos import Modulo
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.roles import Rol
from pjecz_hercules_api_key.models.sentencias import Sentencia
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.models.usuarios_roles import UsuarioRol

__all__ = [
    "Autoridad",
    "Distrito",
    "Edicto",
    "Glosa",
    "ListaDeAcuerdo",
    "Materia",
    "MateriaTipoJuicio",
    "Modulo",
    "Permiso",
    "Rol",
    "Sentencia",
    "Usuario",
    "UsuarioRol",
]
