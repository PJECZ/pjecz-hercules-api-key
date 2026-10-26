"""
Archivos Documentos Tipos
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.core.database import Base


class ArcDocumentoTipo(Base):
    """ArcDocumentoTipo"""

    # Nombre de la tabla
    __tablename__ = "arc_documentos_tipos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[str] = mapped_column(String(32), unique=True)

    # Hijos
    arc_documentos: Mapped[list["ArcDocumento"]] = relationship(back_populates="arc_documento_tipo")
    arc_remesas: Mapped[list["ArcRemesa"]] = relationship(back_populates="arc_documento_tipo")

    def __repr__(self):
        """Representación"""
        return f"<ArcDocumentoTipo {self.id}>"
