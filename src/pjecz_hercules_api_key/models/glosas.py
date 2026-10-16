"""
Glosas
"""

from datetime import date

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.core.database import Base


class Glosa(Base):
    """Glosa"""

    TIPOS_JUICIOS = {
        "ND": "No Definido",
        "AMPARO": "Amparo",
        "EJECUCION": "Ejecución",
        "JUICIO ORAL": "Juicio Oral",
        "JUICIO DE NULIDAD": "Juicio de Nulidad",
        "LABORAL LAUDO": "Laboral Laudo",
        "ORAL": "Oral",
        "PENAL": "Penal",
        "SALA CIVIL": "Sala Civil",
        "SALA CIVIL Y FAMILIAR": "Sala Civil y Familiar",
        "TRADICIONAL": "Tradicional",
    }

    # Nombre de la tabla
    __tablename__ = "glosas"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="glosas")

    # Columnas
    fecha: Mapped[date]
    tipo_juicio: Mapped[str] = mapped_column(Enum(*TIPOS_JUICIOS, name="glosas_tipos_juicios", native_enum=False), index=True)
    descripcion: Mapped[str] = mapped_column(String(256))
    expediente: Mapped[str] = mapped_column(String(16))
    archivo: Mapped[str] = mapped_column(String(256))
    url: Mapped[str] = mapped_column(String(512))

    @property
    def distrito_clave(self):
        """Distrito clave"""
        return self.autoridad.distrito.clave

    @property
    def distrito_nombre(self):
        """Distrito nombre"""
        return self.autoridad.distrito.nombre

    @property
    def distrito_nombre_corto(self):
        """Distrito nombre corto"""
        return self.autoridad.distrito.nombre_corto

    @property
    def autoridad_clave(self):
        """Autoridad clave"""
        return self.autoridad.clave

    @property
    def autoridad_descripcion(self):
        """Autoridad descripción"""
        return self.autoridad.descripcion

    @property
    def autoridad_descripcion_corta(self):
        """Autoridad descripción corta"""
        return self.autoridad.descripcion_corta

    def __repr__(self):
        """Representación"""
        return f"<Glosa {self.id}>"
