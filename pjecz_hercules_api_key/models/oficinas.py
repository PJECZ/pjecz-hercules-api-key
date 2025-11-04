"""
Oficinas, modelos
"""

from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies.database import Base
from ..dependencies.universal_mixin import UniversalMixin
from .distritos import Distrito
from .domicilios import Domicilio
from .funcionarios_oficinas import FuncionarioOficina
from .usuarios import Usuario


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

    def __repr__(self):
        """Representación"""
        return f"<Oficina {self.clave}>"
