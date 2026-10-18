"""
Models

Importa todos los modelos para que SQLAlchemy pueda resolver las relaciones declaradas con nombres de clase.
"""

from pjecz_hercules_api_key.models.arc_documentos import ArcDocumento
from pjecz_hercules_api_key.models.arc_documentos_tipos import ArcDocumentoTipo
from pjecz_hercules_api_key.models.arc_juzgados_extintos import ArcJuzgadoExtinto
from pjecz_hercules_api_key.models.arc_remesas import ArcRemesa
from pjecz_hercules_api_key.models.arc_remesas_documentos import ArcRemesaDocumento
from pjecz_hercules_api_key.models.autoridades import Autoridad
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.domicilios import Domicilio
from pjecz_hercules_api_key.models.edictos import Edicto
from pjecz_hercules_api_key.models.glosas import Glosa
from pjecz_hercules_api_key.models.listas_de_acuerdos import ListaDeAcuerdo
from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_api_key.models.modulos import Modulo
from pjecz_hercules_api_key.models.ofi_documentos import OfiDocumento
from pjecz_hercules_api_key.models.ofi_documentos_adjuntos import OfiDocumentoAdjunto
from pjecz_hercules_api_key.models.ofi_documentos_destinatarios import OfiDocumentoDestinatario
from pjecz_hercules_api_key.models.oficinas import Oficina
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.roles import Rol
from pjecz_hercules_api_key.models.sentencias import Sentencia
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.models.usuarios_roles import UsuarioRol

__all__ = [
    "ArcDocumento",
    "ArcDocumentoTipo",
    "ArcJuzgadoExtinto",
    "ArcRemesa",
    "ArcRemesaDocumento",
    "Autoridad",
    "Distrito",
    "Domicilio",
    "Edicto",
    "Glosa",
    "ListaDeAcuerdo",
    "Materia",
    "MateriaTipoJuicio",
    "Modulo",
    "OfiDocumento",
    "OfiDocumentoAdjunto",
    "OfiDocumentoDestinatario",
    "Oficina",
    "Permiso",
    "Rol",
    "Sentencia",
    "Usuario",
    "UsuarioRol",
]
