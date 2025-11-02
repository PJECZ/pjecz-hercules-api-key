"""
Exh Exhortos, modelos
"""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies.database import Base
from ..dependencies.universal_mixin import UniversalMixin
from ..models.exh_areas import ExhArea
from ..models.exh_exhortos_archivos import ExhExhortoArchivo
from ..models.exh_exhortos_partes import ExhExhortoParte
from ..models.exh_tipos_diligencias import ExhTipoDiligencia
from ..models.municipios import Municipio


class ExhExhorto(Base, UniversalMixin):
    """ExhExhorto"""

    ESTADOS = {
        "RECIBIDO": "Recibido",
        "TRANSFIRIENDO": "Transfiriendo",
        "PROCESANDO": "Procesando",
        "RECHAZADO": "Rechazado",
        "CONTESTADO": "Contestado",
        "PENDIENTE": "Pendiente",
        "CANCELADO": "Cancelado",
        "POR ENVIAR": "Por enviar",
        "RECIBIDO CON EXITO": "Recibido con éxito",
        "RESPONDIDO": "Respondido",
        "ARCHIVADO": "Archivado",
    }

    REMITENTES = {
        "INTERNO": "Interno",
        "EXTERNO": "Externo",
    }

    # Nombre de la tabla
    __tablename__ = "exh_exhortos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea: Autoridad, Juzgado/Área al que se turna el Exhorto y hará el correspondiente proceso de este
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="exh_exhortos")

    # Clave foránea: Área de recepción
    exh_area_id: Mapped[int] = mapped_column(ForeignKey("exh_areas.id"))
    exh_area: Mapped["ExhArea"] = relationship(back_populates="exh_exhortos")

    # Clave foránea: Tipo de diligencia
    exh_tipo_diligencia_id: Mapped[int] = mapped_column(ForeignKey("exh_tipos_diligencias.id"))
    exh_tipo_diligencia: Mapped["ExhTipoDiligencia"] = relationship(back_populates="exh_exhortos")

    # Clave foránea: Municipio de Origen donde está localizado el Juzgado del PJ exhortante
    # Cuando haya comunicación por medio de la API se debe recibir o transmitir el identificador INEGI del municipio
    municipio_origen_id: Mapped[int] = mapped_column(ForeignKey("municipios.id"))
    municipio_origen: Mapped["Municipio"] = relationship(back_populates="exh_exhortos_origenes")

    # UUID identificador con el que el PJ exhortante identifica el exhorto que envía
    exhorto_origen_id: Mapped[str] = mapped_column(String(64))

    # ID del municipio del Estado del PJ exhortado al que se quiere enviar el Exhorto
    # NO es una clave foránea para no causar conflicto con municipio_origen_id
    municipio_destino_id: Mapped[int]

    # Materia (el que se obtuvo en la consulta de materias del PJ exhortado) al que el Exhorto hace referencia
    materia_clave: Mapped[str] = mapped_column(String(32))
    materia_nombre: Mapped[str] = mapped_column(String(256))

    # Identificador propio y nombre del Juzgado/Área que envía el Exhorto
    juzgado_origen_id: Mapped[Optional[str]] = mapped_column(String(64))
    juzgado_origen_nombre: Mapped[str] = mapped_column(String(256))

    # El número de expediente (o carpeta procesal, carpeta...) que tiene el asunto en el Juzgado de Origen
    numero_expediente_origen: Mapped[str] = mapped_column(String(256))

    # Nombre del tipo de Juicio, o asunto, listado de los delitos (para materia Penal)
    # que corresponde al Expediente del cual el Juzgado envía el Exhorto
    tipo_juicio_asunto_delitos: Mapped[str] = mapped_column(String(256))

    # Número de fojas que contiene el exhorto. El valor 0 significa "No Especificado"
    fojas: Mapped[int]

    # Cantidad de dias a partir del día que se recibió en el Poder Judicial exhortado que se tiene para responder el Exhorto.
    # El valor de 0 significa "No Especificado"
    dias_responder: Mapped[int]

    # Campo para saber si es un proceso interno o extorno
    remitente: Mapped[str] = mapped_column(Enum(*REMITENTES, name="exh_exhortos_remitentes", native_enum=False), index=True)

    # Estado del exhorto y el estado anterior, para cuando
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="exh_exhortos_estados", native_enum=False), index=True)

    # Hijo: Partes
    # Contiene la definición de las partes del Expediente/Juicio/Asunto en el Juzgado/Área de origen
    exh_exhortos_partes: Mapped[List["ExhExhortoParte"]] = relationship("ExhExhortoParte", back_populates="exh_exhorto")
    # Hijo: Archivos
    # Colección de los datos referentes a los archivos que se van a recibir el Poder Judicial exhortado en el envío del Exhorto.
    exh_exhortos_archivos: Mapped[List["ExhExhortoArchivo"]] = relationship("ExhExhortoArchivo", back_populates="exh_exhorto")

    @property
    def autoridad_clave(self):
        """Regresa la clave de la autoridad"""
        return self.autoridad.clave

    @property
    def exh_area_clave(self):
        """Regresa la clave del área de recepción"""
        return self.exh_area.clave

    @property
    def municipio_origen_clave(self):
        """Regresa el clave del municipio de origen"""
        return self.municipio_origen.clave

    @property
    def municipio_origen_nombre(self):
        """Regresa el nombre del municipio de origen"""
        return self.municipio_origen.nombre

    @property
    def municipio_destino_clave(self):
        """Regresa la clave del municipio de destino"""
        return self.autoridad.municipio.clave

    @property
    def municipio_destino_nombre(self):
        """Regresa el nombre del municipio de destino"""
        return self.autoridad.municipio.nombre

    def __repr__(self):
        """Representación"""
        return f"<ExhExhorto {self.id}>"
