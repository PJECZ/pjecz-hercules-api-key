"""
Municipios
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.core.database import Base


class Municipio(Base):
    """Municipio"""

    # Nombre de la tabla
    __tablename__ = "municipios"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    estado_id: Mapped[int] = mapped_column(ForeignKey("estados.id"))
    estado: Mapped["Estado"] = relationship(back_populates="municipios")

    # Columnas
    clave: Mapped[str] = mapped_column(String(3))
    nombre: Mapped[str] = mapped_column(String(256))

    # Hijos
    autoridades: Mapped[list["Autoridad"]] = relationship("Autoridad", back_populates="municipio")
    exh_exhortos_origenes: Mapped[list["ExhExhorto"]] = relationship("ExhExhorto", back_populates="municipio_origen")

    @property
    def estado_clave(self):
        """Clave del estado"""
        return self.estado.clave

    @property
    def estado_nombre(self):
        """Nombre del estado"""
        return self.estado.nombre

    def __repr__(self):
        """Representación"""
        return f"<Municipio {self.estado.clave}{self.clave}>"
