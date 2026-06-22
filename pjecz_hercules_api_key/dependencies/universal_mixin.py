"""
UniversalMixin define las columnas y métodos comunes de todos los modelos
"""

import re
from datetime import datetime

from hashids import Hashids
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import now
from sqlalchemy.types import CHAR

from pjecz_hercules_api_key.config.settings import get_settings

settings = get_settings()
hashids = Hashids(salt=settings.SALT, min_length=8)


class UniversalMixin:
    """Columnas y métodos comunes a todas las tablas"""

    creado: Mapped[datetime] = mapped_column(default=now())
    modificado: Mapped[datetime] = mapped_column(default=now(), onupdate=now())
    estatus: Mapped[str] = mapped_column(CHAR, default="A")

    def encode_id(self):
        """Convertir el ID de entero a cadena"""
        return hashids.encode(self.id)

    @classmethod
    def decode_id(cls, id_encoded: str):
        """Convertir el ID de entero a cadena"""
        if re.fullmatch(r"[0-9a-zA-Z]{8,16}", id_encoded) is None:
            return None
        descifrado = hashids.decode(id_encoded)
        if len(descifrado) == 0:
            return None
        return descifrado[0]
