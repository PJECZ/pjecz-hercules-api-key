"""
Oficinas, modelos
"""

from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.dependencies.database import Base
from pjecz_hercules_api_key.dependencies.universal_mixin import UniversalMixin


class Oficina(Base, UniversalMixin):
    """Oficina"""

    # Nombre de la tabla
    __tablename__ = "oficinas"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    distrito_id: Mapped[int] = mapped_column(ForeignKey("distritos.id"))
    distrito: Mapped["Distrito"] = relationship(back_populates="oficinas")
    domicilio_id: Mapped[int] = mapped_column(ForeignKey("domicilios.id"))
    domicilio: Mapped["Domicilio"] = relationship(back_populates="oficinas")

    # Columnas
    clave: Mapped[str] = mapped_column(String(32), unique=True)
    descripcion: Mapped[str] = mapped_column(String(512))
    descripcion_corta: Mapped[str] = mapped_column(String(64))
    es_jurisdiccional: Mapped[bool] = mapped_column(default=False)

    # Hijos
    funcionarios_oficinas: Mapped[List["FuncionarioOficina"]] = relationship(back_populates="oficina")
    usuarios: Mapped[List["Usuario"]] = relationship("Usuario", back_populates="oficina")

    @property
    def distrito_clave(self):
        """Clave del distrito"""
        return self.distrito.clave

    @property
    def distrito_nombre(self):
        """Nombre del distrito"""
        return self.distrito.nombre

    @property
    def domicilio_edificio(self):
        """Edificio del domicilio"""
        return self.domicilio.edificio

    def __repr__(self):
        """Representación"""
        return f"<Oficina {self.clave}>"
