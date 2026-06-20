"""
Archivos Juzgados Extintos
"""

from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.dependencies.database import Base
from pjecz_hercules_api_key.dependencies.universal_mixin import UniversalMixin


class ArcJuzgadoExtinto(Base, UniversalMixin):
    """ArcJuzgadoExtinto"""

    # Nombre de la tabla
    __tablename__ = "arc_juzgados_extintos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    distrito_id: Mapped[int] = mapped_column(ForeignKey("distritos.id"))
    distrito: Mapped["Distrito"] = relationship(back_populates="arc_juzgados_extintos")

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    descripcion_corta: Mapped[str] = mapped_column(String(64))
    descripcion: Mapped[str] = mapped_column(String(256))

    # Hijos
    arc_documentos: Mapped[List["ArcDocumento"]] = relationship(back_populates="arc_juzgado_origen")

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

    def __repr__(self):
        """Representación"""
        return f"<ArcJuzgadoExtinto {self.id}>"
