"""
Database

Entrega sesiones SQLAlchemy 2.0 reutilizables hacia PostgreSQL.

Uso en FastAPI:

    from fastapi import Depends
    from sqlalchemy.orm import Session
    from .database import get_session

    @app.get("/items")
    def listar(session: Session = Depends(get_session)):
        ...

Uso en línea de comandos (Typer, scripts, workers):

    from .database import session_scope

    with session_scope() as session:
        session.add(objeto)
        # commit automático al salir; rollback si hay excepción
"""

import re
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from functools import lru_cache

from hashids import Hashids
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.sql.functions import now
from sqlalchemy.types import CHAR

from pjecz_hercules_api_key.config.setttings import get_settings

settings = get_settings()
hashids = Hashids(salt=settings.SALT, min_length=8)


class Base(DeclarativeBase):
    """Clase base declarativa de la que heredan todos los modelos."""

    creado: Mapped[datetime] = mapped_column(default=now(), server_default=now())
    modificado: Mapped[datetime] = mapped_column(default=now(), onupdate=now(), server_default=now())
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


@lru_cache
def get_engine() -> Engine:
    """Crear el engine una sola vez por proceso"""
    settings = get_settings()
    return create_engine(
        settings.database_uri,
        pool_size=10,  # Conexiones permanentes en el pool
        max_overflow=20,  # Conexiones extra temporales
        pool_pre_ping=True,  # Verifica la conexión antes de usarla
        pool_recycle=1800,  # Recicla conexiones cada 30 minutos
        echo=False,  # True para ver el SQL en desarrollo
    )


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    """Fábrica de sesiones ligada al engine"""
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


def get_session() -> Generator[Session, None, None]:
    """Dependencia para FastAPI: entrega una sesión y la cierra al terminar"""
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager transaccional: commit al salir, rollback si hay error"""
    session = get_sessionmaker()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def dispose_engine() -> None:
    """Liberar el pool de conexiones (al apagar la app o tras un fork de workers)"""
    get_engine().dispose()
    get_sessionmaker.cache_clear()
    get_engine.cache_clear()
