"""
Funcionarios, modelos
"""

from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.dependencies.database import Base
from pjecz_hercules_api_key.dependencies.universal_mixin import UniversalMixin


class Funcionario(Base, UniversalMixin):
    """Funcionario"""

    # Nombre de la tabla
    __tablename__ = "funcionarios"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombres: Mapped[str] = mapped_column(String(256))
    apellido_paterno: Mapped[str] = mapped_column(String(256))
    apellido_materno: Mapped[str] = mapped_column(String(256), default="")
    curp: Mapped[str] = mapped_column(String(18), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    puesto: Mapped[str] = mapped_column(String(256), default="")
    en_funciones: Mapped[bool] = mapped_column(default=True)
    en_soportes: Mapped[bool] = mapped_column(default=False)

    # Hijos
    funcionarios_oficinas: Mapped[List["FuncionarioOficina"]] = relationship(back_populates="funcionario")
    soportes_tickets: Mapped[List["SoporteTicket"]] = relationship(back_populates="funcionario")

    @property
    def nombre(self):
        """Junta nombres, apellido_paterno y apellido materno"""
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

    def __repr__(self):
        """Representación"""
        return f"<Funcionario {self.nombre}>"
