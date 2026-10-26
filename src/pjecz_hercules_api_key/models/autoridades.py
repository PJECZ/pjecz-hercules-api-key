"""
Autoridades
"""

from typing import Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.core.database import Base


class Autoridad(Base):
    """Autoridad"""

    ORGANOS_JURISDICCIONALES = {
        "NO DEFINIDO": "No Definido",
        "JUZGADO DE PRIMERA INSTANCIA": "Juzgado de Primera Instancia",
        "JUZGADO DE PRIMERA INSTANCIA ORAL": "Juzgado de Primera Instancia Oral",
        "PLENO O SALA DEL TSJ": "Pleno o Sala del TSJ",
        "TRIBUNAL DISTRITAL": "Tribunal Distrital",
        "TRIBUNAL DE CONCILIACION Y ARBITRAJE": "Tribunal de Conciliación y Arbitraje",
    }

    # Nombre de la tabla
    __tablename__ = "autoridades"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    distrito_id: Mapped[int] = mapped_column(ForeignKey("distritos.id"))
    distrito: Mapped["Distrito"] = relationship(back_populates="autoridades")
    materia_id: Mapped[int] = mapped_column(ForeignKey("materias.id"))
    materia: Mapped["Materia"] = relationship(back_populates="autoridades")
    municipio_id: Mapped[int] = mapped_column(ForeignKey("municipios.id"))
    municipio: Mapped["Municipio"] = relationship(back_populates="autoridades")

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    descripcion: Mapped[str] = mapped_column(String(256))
    descripcion_corta: Mapped[str] = mapped_column(String(64))
    directorio_edictos: Mapped[str] = mapped_column(String(256))
    directorio_glosas: Mapped[str] = mapped_column(String(256))
    directorio_listas_de_acuerdos: Mapped[str] = mapped_column(String(256))
    directorio_sentencias: Mapped[str] = mapped_column(String(256))
    es_archivo_solicitante: Mapped[bool] = mapped_column(default=False)
    es_cemasc: Mapped[bool] = mapped_column(default=False)
    es_defensoria: Mapped[bool] = mapped_column(default=False)
    es_extinto: Mapped[bool] = mapped_column(default=False)
    es_jurisdiccional: Mapped[bool] = mapped_column(default=False)
    es_notaria: Mapped[bool] = mapped_column(default=False)
    es_organo_especializado: Mapped[bool] = mapped_column(default=False)
    es_revisor_escrituras: Mapped[bool] = mapped_column(default=False)
    organo_jurisdiccional: Mapped[str] = mapped_column(
        Enum(*ORGANOS_JURISDICCIONALES, name="autoridades_organos_jurisdiccionales", native_enum=False),
        index=True,
    )

    # Hijos
    arc_documentos: Mapped[list["ArcDocumento"]] = relationship(back_populates="autoridad")
    arc_remesas: Mapped[list["ArcRemesa"]] = relationship(back_populates="autoridad")
    dgt_digitalizaciones: Mapped[list["DgtDigitalizacion"]] = relationship(back_populates="autoridad")
    dgt_plataforma_autoridad: Mapped[Optional["DgtPlataformaAutoridad"]] = relationship(back_populates="autoridad")  # Uno a uno
    dgt_entregas: Mapped[list["DgtEntrega"]] = relationship(back_populates="autoridad")
    edictos: Mapped[list["Edicto"]] = relationship(back_populates="autoridad")
    exh_exhortos: Mapped[list["ExhExhorto"]] = relationship(back_populates="autoridad")
    glosas: Mapped[list["Glosa"]] = relationship(back_populates="autoridad")
    listas_de_acuerdos: Mapped[list["ListaDeAcuerdo"]] = relationship(back_populates="autoridad")
    redam: Mapped[list["Redam"]] = relationship(back_populates="autoridad")
    sentencias: Mapped[list["Sentencia"]] = relationship(back_populates="autoridad")
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="autoridad")

    @property
    def distrito_clave(self):
        """Clave del distrito"""
        return self.distrito.clave

    @property
    def distrito_nombre(self):
        """Nombre del distrito"""
        return self.distrito.nombre

    @property
    def distrito_nombre_corto(self):
        """Nombre corto del distrito"""
        return self.distrito.nombre_corto

    @property
    def materia_clave(self):
        """Clave de la materia"""
        return self.materia.clave

    @property
    def materia_nombre(self):
        """Nombre de la materia"""
        return self.materia.nombre

    def __repr__(self):
        """Representación"""
        return f"<Autoridad {self.clave}>"
