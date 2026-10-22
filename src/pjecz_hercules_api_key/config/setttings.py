"""
Settings
"""

import os
from functools import lru_cache
from typing import Any

from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class SecretManagerSettingsSource(PydanticBaseSettingsSource):
    """Fuente de configuración desde Google Cloud Secret Manager"""

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        """No se usa, __call__ arma el diccionario completo"""
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        """Obtener los valores de los secretos si PROJECT_ID está definido"""
        project_id = os.environ.get("PROJECT_ID", "")
        if not project_id:
            return {}

        service_prefix = os.environ.get("SERVICE_PREFIX", "")
        if not service_prefix:
            raise ValueError("SERVICE_PREFIX is required when PROJECT_ID is set")

        from google.api_core.exceptions import NotFound
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        data: dict[str, Any] = {}
        for field_name in self.settings_cls.model_fields:
            secret_id = f"{service_prefix}_{field_name}".lower()
            name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
            try:
                response = client.access_secret_version(name=name)
            except NotFound:
                continue
            data[field_name] = response.payload.data.decode("utf-8").strip()
        return data


class Settings(BaseSettings):
    """Settings"""

    API_KEY_CUOTA_DIARIA: int = 1000
    API_NOMBRE: str = "pjecz-hercules-api-key"
    DB_USER: str = ""
    DB_PASS: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_NAME: str = ""
    ESTADO_CLAVE: str = "05"
    GCP_BUCKET_EDICTOS: str = ""
    GCP_BUCKET_GLOSAS: str = ""
    GCP_BUCKET_LISTAS_DE_ACUERDOS: str = ""
    GCP_BUCKET_OFICIOS: str = ""
    GCP_BUCKET_SENTENCIAS: str = ""
    SALT: str = ""
    SQLALCHEMY_DATABASE_URI: str = ""
    TZ: str = "America/Mexico_City"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def build_database_uri(self) -> str:
        """Construye la URI cuando no está provista directamente."""
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI

        if not (self.DB_USER and self.DB_PASS and self.DB_NAME):
            return "postgresql+psycopg2://localhost:5432/postgres"

        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST or '127.0.0.1'}:{self.DB_PORT or '5432'}/{self.DB_NAME}"
        )

    @property
    def database_uri(self) -> str:
        """URI de la base de datos PostgreSQL."""
        return self.build_database_uri()


@lru_cache
def get_settings() -> Settings:
    """Get settings"""
    return Settings()
