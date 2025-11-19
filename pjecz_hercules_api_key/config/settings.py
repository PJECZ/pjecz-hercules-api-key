"""
Settings
"""

import os
from functools import lru_cache

import google.auth
from google.cloud import secretmanager
from pydantic_settings import BaseSettings

PROJECT_ID = os.getenv("PROJECT_ID", "")  # Por defecto esta vacio, esto significa estamos en modo local
SERVICE_PREFIX = os.getenv("SERVICE_PREFIX", "pjecz_plataforma_web_api_key")


def get_secret(secret_id: str, default: str = "") -> str:
    """Get secret from Google Cloud Secret Manager"""

    # Si PROJECT_ID está vacío estamos en modo de desarrollo y debe usar las variables de entorno
    if PROJECT_ID == "":
        # Entregar el valor de la variable de entorno, si no esta definida, se entrega el valor por defecto
        value = os.getenv(secret_id.upper(), "")
        if value == "":
            return default
        return value

    # Obtener el project_id con la librería de Google Auth
    _, project_id = google.auth.default()

    # Si NO estamos en Google Cloud, entonces se está ejecutando de forma local
    if not project_id:
        # Entregar el valor de la variable de entorno, si no esta definida, se entrega el valor por defecto
        value = os.getenv(secret_id.upper())
        if value is None:
            return default
        return value

    # Tratar de obtener el secreto
    try:
        # Create the secret manager client
        client = secretmanager.SecretManagerServiceClient()
        # Build the resource name of the secret version
        secret = f"{SERVICE_PREFIX}_{secret_id}"
        name = client.secret_version_path(project_id, secret, "latest")
        # Access the secret version
        response = client.access_secret_version(name=name)
        # Return the decoded payload
        return response.payload.data.decode("UTF-8")
    except:
        pass

    # Entregar el valor por defecto porque no existe el secreto, ni la variable de entorno
    return default


class Settings(BaseSettings):
    """Settings"""

    DB_HOST: str = get_secret("db_host")
    DB_PORT: int = int(get_secret("db_port"))
    DB_NAME: str = get_secret("db_name")
    DB_PASS: str = get_secret("db_pass")
    DB_USER: str = get_secret("db_user")
    ESTADO_CLAVE: str = get_secret("estado_clave", "05")  # Por defecto es Coahuila de Zaragoza
    GCP_BUCKET: str = get_secret("gcp_bucket")
    GCP_BUCKET_EDICTOS: str = get_secret("gcp_bucket_edictos")
    GCP_BUCKET_GLOSAS: str = get_secret("gcp_bucket_glosas")
    GCP_BUCKET_LISTAS_DE_ACUERDOS: str = get_secret("gcp_bucket_listas_de_acuerdos")
    GCP_BUCKET_SENTENCIAS: str = get_secret("gcp_bucket_sentencias")
    ORIGINS: str = get_secret("origins")
    SALT: str = get_secret("salt")
    TZ: str = "America/Mexico_City"

    class Config:
        """Load configuration"""

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            """Customise sources, first environment variables, then .env file, then google cloud secret manager"""
            return env_settings, file_secret_settings, init_settings


@lru_cache()
def get_settings() -> Settings:
    """Get Settings"""
    return Settings()
