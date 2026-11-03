"""
Audiencias
"""

from datetime import datetime

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_api_key.core.database import Base


class Audiencia(Base):
    """Audiencia"""

    CARACTERES = {
        "NO DEFINIDO": "No definido",
        "PUBLICA": "Pública",
        "PRIVADA": "Privada",
    }

    # Nombre de la tabla
    __tablename__ = "audiencias"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="audiencias")

    # Columnas comunes
    tiempo: Mapped[datetime]
    tipo_audiencia: Mapped[str] = mapped_column(String(256), default="")

    # Columnas para Materias C F M L D(CyF) Salas (CyF) TCyA
    expediente: Mapped[str] = mapped_column(String(64), default="")
    actores: Mapped[str] = mapped_column(String(256), default="")
    demandados: Mapped[str] = mapped_column(String(256), default="")

    # Columnas para Materia Acusatorio Penal Oral
    sala: Mapped[str] = mapped_column(String(256), default="")
    caracter: Mapped[str] = mapped_column(Enum(*CARACTERES, name="tipos_caracteres", native_enum=False), default="NO DEFINIDO")
    causa_penal: Mapped[str] = mapped_column(String(256), default="")
    delitos: Mapped[str] = mapped_column(String(256), default="")

    # Columnas para Distritales Penales
    toca: Mapped[str] = mapped_column(String(256), default="")
    expediente_origen: Mapped[str] = mapped_column(String(256), default="")
    imputados: Mapped[str] = mapped_column(String(256), default="")

    # Columnas para Salas Penales
    # toca
    # expediente_origen
    # delitos
    origen: Mapped[str] = mapped_column(String(256), default="")

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
        return f"<Audiencia {self.id}>"
