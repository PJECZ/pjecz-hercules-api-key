"""
Programa principal: arrancar FastAPI con Uvicorn

Equivale al comando:

    uvicorn --host=127.0.0.1 --port 8000 --reload pjecz_hercules_api_key.app:app
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("pjecz_hercules_api_key.app:app", host="127.0.0.1", port=8000, reload=True)
