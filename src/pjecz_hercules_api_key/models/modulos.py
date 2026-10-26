"""
Módulos
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.core.database import Base


class Modulo(Base):
    """Modulo"""

    # Nombre de la tabla
    __tablename__ = "modulos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[str] = mapped_column(String(256), unique=True)
    nombre_corto: Mapped[str] = mapped_column(String(64))
    icono: Mapped[str] = mapped_column(String(48))
    ruta: Mapped[str] = mapped_column(String(64))
    en_navegacion: Mapped[bool] = mapped_column(default=False)

    # Hijos
    permisos: Mapped[list["Permiso"]] = relationship(back_populates="modulo")

    def __repr__(self):
        """Representación"""
        return f"<Modulo {self.nombre}>"
