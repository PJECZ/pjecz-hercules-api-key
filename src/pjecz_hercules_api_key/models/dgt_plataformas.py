"""
DGT Plataformas
"""

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.core.database import Base


class DgtPlataforma(Base):
    """DgtPlataforma"""

    # Nombre de la tabla
    __tablename__ = "dgt_plataformas"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Columnas
    descripcion: Mapped[str] = mapped_column(String(256), unique=True)

    # Hijos
    dgt_plataformas_autoridades: Mapped[list["DgtPlataformaAutoridad"]] = relationship(back_populates="dgt_plataforma")
    dgt_plataformas_endpoints: Mapped[list["DgtPlataformaEndpoint"]] = relationship(back_populates="dgt_plataforma")

    def __repr__(self):
        """Representación"""
        return f"<DgtPlataforma {self.id}>"
