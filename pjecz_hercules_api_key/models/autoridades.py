"""
Autoridades, modelos
"""

from typing import List

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies.database import Base
from ..dependencies.universal_mixin import UniversalMixin


class Autoridad(Base, UniversalMixin):
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

    # Clave foránea
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
    es_extinto: Mapped[bool] = mapped_column(default=False)
    es_cemasc: Mapped[bool] = mapped_column(default=False)
    es_defensoria: Mapped[bool] = mapped_column(default=False)
    es_jurisdiccional: Mapped[bool] = mapped_column(default=False)
    es_notaria: Mapped[bool] = mapped_column(default=False)
    es_organo_especializado: Mapped[bool] = mapped_column(default=False)
    organo_jurisdiccional: Mapped[str] = mapped_column(
        Enum(*ORGANOS_JURISDICCIONALES, name="autoridades_organos_jurisdiccionales", native_enum=False),
        index=True,
    )
    directorio_edictos: Mapped[str] = mapped_column(String(256))
    directorio_glosas: Mapped[str] = mapped_column(String(256))
    directorio_listas_de_acuerdos: Mapped[str] = mapped_column(String(256))
    directorio_sentencias: Mapped[str] = mapped_column(String(256))

    # Hijos
    edictos: Mapped[List["Edicto"]] = relationship("Edicto", back_populates="autoridad")
    exh_exhortos: Mapped[List["ExhExhorto"]] = relationship("ExhExhorto", back_populates="autoridad")
    listas_de_acuerdos: Mapped[List["ListaDeAcuerdo"]] = relationship("ListaDeAcuerdo", back_populates="autoridad")
    sentencias: Mapped[List["Sentencia"]] = relationship("Sentencia", back_populates="autoridad")
    usuarios: Mapped[List["Usuario"]] = relationship("Usuario", back_populates="autoridad")

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

    @property
    def municipio_clave(self):
        """Clave de la municipio"""
        return self.municipio.clave

    @property
    def municipio_nombre(self):
        """Nombre de la municipio"""
        return self.municipio.nombre

    def __repr__(self):
        """Representación"""
        return f"<Autoridad {self.clave}>"
