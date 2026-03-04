"""
Settings
"""

import os
from functools import lru_cache

from google.cloud import secretmanager
from pydantic_settings import BaseSettings


def get_secret(secret_id: str, default: str = "") -> str:
    """Obtener el valor del secreto desde Google Cloud Secret Manager o desde las variables de entorno"""
    project_id = os.getenv("PROJECT_ID", "")
    service_prefix = os.getenv("SERVICE_PREFIX", "pjecz_plataforma_web_api_key")

    # Si PROJECT_ID está vacío estamos en modo de desarrollo
    if project_id == "":
        value = os.getenv(secret_id.upper(), "")
        # Si el valor es texto vacio, entregar el valor por defecto
        if value == "":
            return default
        return value

    # Tratar de obtener el secreto
    try:
        # Create the secret manager client
        client = secretmanager.SecretManagerServiceClient()
        # Build the resource name of the secret version
        secret = f"{service_prefix}_{secret_id}".lower()
        name = client.secret_version_path(project_id, secret, "latest")
        # Access the secret version
        response = client.access_secret_version(name=name)
        # Return the decoded payload
        return response.payload.data.decode("UTF-8")
    except:
        pass

    # Si no funciona lo anterior, entregar el valor por defecto
    return default


class Settings(BaseSettings):
    """Settings"""

    API_NOMBRE: str = get_secret("api_nombre", "pjecz_hercules_api_key")
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
