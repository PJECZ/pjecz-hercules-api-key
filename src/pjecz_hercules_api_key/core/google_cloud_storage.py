"""
Google Cloud Storage

Funciones para obtener el contenido de los archivos guardados en Google Cloud Storage.
Lanzan HTTPException 404 cuando no se encuentra el archivo, 500 si falta configurar el bucket y 503 si falla el servicio.
"""

from urllib.parse import unquote, urlparse

from fastapi import HTTPException, status
from google.api_core.exceptions import GoogleAPIError
from google.cloud import storage


def _validate_bucket_name(bucket_name: str) -> None:
    """Validar que el bucket esté configurado"""
    if not bucket_name:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Missing bucket configuration")


def get_blob_name_from_url(bucket_name: str, url: str) -> str:
    """Obtener el blob_name a partir de la URL, quitando el prefijo /<bucket_name>/"""
    _validate_bucket_name(bucket_name)
    prefijo = f"/{bucket_name}/"
    ruta = urlparse(url).path
    if not ruta.startswith(prefijo):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File URL is not valid")
    blob_name = unquote(ruta[len(prefijo) :])
    if blob_name == "":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File URL is not valid")
    return blob_name


def get_file_from_gcs(bucket_name: str, blob_name: str) -> bytes:
    """Descargar el contenido del archivo en memoria"""
    _validate_bucket_name(bucket_name)
    try:
        client = storage.Client()
        blob = client.bucket(bucket_name).blob(blob_name)
        if not blob.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in storage")
        return blob.download_as_bytes()
    except GoogleAPIError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Storage service unavailable") from error
