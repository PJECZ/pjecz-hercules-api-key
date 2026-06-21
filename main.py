"""
Programa principal
"""

import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()
FASTAPI_APP = os.getenv("FASTAPI_APP", "pjecz_hercules_api_key.app") + ":app"
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "127.0.0.1")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))

if __name__ == "__main__":
    uvicorn.run(FASTAPI_APP, host=FASTAPI_HOST, port=FASTAPI_PORT, reload=True)
