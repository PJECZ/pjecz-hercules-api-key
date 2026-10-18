"""
DGT Plataformas Autoridades
"""

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.core.database import Base


class DgtPlataformaAutoridad(Base):
    """DgtPlataformaAutoridad"""

    # Nombre de la tabla
    __tablename__ = "dgt_plataformas_autoridades"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    # La autoridad es única: cada autoridad sólo puede tener una plataforma
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"), unique=True)
    autoridad: Mapped["Autoridad"] = relationship(back_populates="dgt_plataforma_autoridad")
    dgt_plataforma_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dgt_plataformas.id"), index=True)
    dgt_plataforma: Mapped["DgtPlataforma"] = relationship(back_populates="dgt_plataformas_autoridades")

    def __repr__(self):
        """Representación"""
        return f"<DgtPlataformaAutoridad {self.id}>"
