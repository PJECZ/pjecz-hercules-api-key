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
from pjecz_hercules_api_key.models.dgt_depositos import DgtDepositos
from pjecz_hercules_api_key.models.dgt_digitalizaciones import DgtDigitalizacion
from pjecz_hercules_api_key.models.dgt_entregas import DgtEntrega
from pjecz_hercules_api_key.models.dgt_plataformas import DgtPlataforma
from pjecz_hercules_api_key.models.dgt_plataformas_autoridades import DgtPlataformaAutoridad
from pjecz_hercules_api_key.models.dgt_plataformas_endpoints import DgtPlataformaEndpoint
from pjecz_hercules_api_key.models.dgt_rutas import DgtRuta
from pjecz_hercules_api_key.models.dgt_tipos import DgtTipo
from pjecz_hercules_api_key.models.distritos import Distrito
from pjecz_hercules_api_key.models.domicilios import Domicilio
from pjecz_hercules_api_key.models.edictos import Edicto
from pjecz_hercules_api_key.models.estados import Estado
from pjecz_hercules_api_key.models.exh_areas import ExhArea
from pjecz_hercules_api_key.models.exh_exhortos import ExhExhorto
from pjecz_hercules_api_key.models.exh_exhortos_archivos import ExhExhortoArchivo
from pjecz_hercules_api_key.models.exh_exhortos_partes import ExhExhortoParte
from pjecz_hercules_api_key.models.exh_tipos_diligencias import ExhTipoDiligencia
from pjecz_hercules_api_key.models.funcionarios import Funcionario
from pjecz_hercules_api_key.models.funcionarios_oficinas import FuncionarioOficina
from pjecz_hercules_api_key.models.glosas import Glosa
from pjecz_hercules_api_key.models.listas_de_acuerdos import ListaDeAcuerdo
from pjecz_hercules_api_key.models.materias import Materia
from pjecz_hercules_api_key.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_api_key.models.modulos import Modulo
from pjecz_hercules_api_key.models.municipios import Municipio
from pjecz_hercules_api_key.models.ofi_documentos import OfiDocumento
from pjecz_hercules_api_key.models.ofi_documentos_adjuntos import OfiDocumentoAdjunto
from pjecz_hercules_api_key.models.ofi_documentos_destinatarios import OfiDocumentoDestinatario
from pjecz_hercules_api_key.models.oficinas import Oficina
from pjecz_hercules_api_key.models.permisos import Permiso
from pjecz_hercules_api_key.models.redams import Redam
from pjecz_hercules_api_key.models.repsvm_agresores import RepsvmAgresor
from pjecz_hercules_api_key.models.roles import Rol
from pjecz_hercules_api_key.models.sentencias import Sentencia
from pjecz_hercules_api_key.models.soportes_categorias import SoporteCategoria
from pjecz_hercules_api_key.models.soportes_tickets import SoporteTicket
from pjecz_hercules_api_key.models.usuarios import Usuario
from pjecz_hercules_api_key.models.usuarios_roles import UsuarioRol

__all__ = [
    "ArcDocumento",
    "ArcDocumentoTipo",
    "ArcJuzgadoExtinto",
    "ArcRemesa",
    "ArcRemesaDocumento",
    "Autoridad",
    "DgtDepositos",
    "DgtDigitalizacion",
    "DgtEntrega",
    "DgtPlataforma",
    "DgtPlataformaAutoridad",
    "DgtPlataformaEndpoint",
    "DgtRuta",
    "DgtTipo",
    "Distrito",
    "Domicilio",
    "Edicto",
    "Estado",
    "ExhArea",
    "ExhExhorto",
    "ExhExhortoArchivo",
    "ExhExhortoParte",
    "ExhTipoDiligencia",
    "Funcionario",
    "FuncionarioOficina",
    "Glosa",
    "ListaDeAcuerdo",
    "Materia",
    "MateriaTipoJuicio",
    "Modulo",
    "Municipio",
    "OfiDocumento",
    "OfiDocumentoAdjunto",
    "OfiDocumentoDestinatario",
    "Oficina",
    "Permiso",
    "Redam",
    "RepsvmAgresor",
    "Rol",
    "Sentencia",
    "SoporteCategoria",
    "SoporteTicket",
    "Usuario",
    "UsuarioRol",
]
