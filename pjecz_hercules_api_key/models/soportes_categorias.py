"""
Soportes Categorias, modelos
"""

from typing import List, Optional

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies.database import Base
from ..dependencies.universal_mixin import UniversalMixin


class SoporteCategoria(Base, UniversalMixin):
    """Soporte Categoria"""

    DEPARTAMENTOS = {
        "TODOS": "Todos",
        "INFORMATICA": "Informatica",
        "INFRAESTRUCTURA": "Infraestructura",
    }

    # Nombre de la tabla
    __tablename__ = "soportes_categorias"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[str] = mapped_column(String(256), unique=True)
    instrucciones: Mapped[str] = mapped_column(Text)
    departamento: Mapped[Optional[str]] = mapped_column(
        Enum(*DEPARTAMENTOS, name="soportes_categorias_departamentos", native_enum=False),
        index=True,
    )

    # Hijos
    soportes_tickets: Mapped[List["SoporteTicket"]] = relationship(back_populates="soporte_categoria")

    def __repr__(self):
        """Representación"""
        return f"<SoporteCategoria {self.id}>"
