# pjecz-hercules-api-key

API de uso público para consultar edictos, listas de acuerdos, sentencias, etc.

Para solicitar un _api-key_ escriba a `informatica` en `pjecz.gob.mx`.

## Requerimientos

Los requerimientos son

- Python 3.11
- PostgreSQL 15

## Instalación

Crear el entorno virtual

```bash
python3.11 -m venv .venv
```

Ingresar al entorno virtual

```bash
source venv/bin/activate
```

Actualizar el gestor de paquetes **pip**

```bash
pip install --upgrade pip setuptools
```

Instalar el paquete **wheel** para compilar las dependencias

```bash
pip install wheel
```

Instalar **poetry 2** en el entorno virtual si no lo tiene desde el sistema operativo

```bash
pip install poetry
```

Configurar **poetry** para que use el entorno virtual dentro del directorio del proyecto

```bash
poetry config virtualenvs.in-project true
```

Instalar las dependencias por medio de **poetry**

```bash
poetry install
```

## Configuración

Crear un archivo `.env` en la raíz del proyecto con las variables de entorno

```ini
# Base de datos
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=pjecz_plataforma_web
DB_USER=XXXXXXXXXXXX
DB_PASS=XXXXXXXXXXXX

# Google Cloud Storage
CLOUD_STORAGE_DEPOSITO=XXXXXXXXXXXX
CLOUD_STORAGE_DEPOSITO_EDICTOS=XXXXXXXXXXXX
CLOUD_STORAGE_DEPOSITO_GLOSAS=XXXXXXXXXXXX
CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS=XXXXXXXXXXXX
CLOUD_STORAGE_DEPOSITO_SENTENCIAS=XXXXXXXXXXXX
CLOUD_STORAGE_DEPOSITO_USUARIOS=XXXXXXXXXXXX

# Origins
ORIGINS=http://localhost:3000

# Salt sirve para cifrar el ID con HashID, debe ser igual en la API
SALT=XXXXXXXXXXXX
```

Crear un archivo `.bashrc` que cargue las variables de entorno y el entorno virtual

```bash
if [ -f ~/.bashrc ]
then
    . ~/.bashrc
fi

if command -v figlet &> /dev/null
then
    figlet Hercules API key
else
    echo "== Hercules API key"
fi
echo

if [ -f .env ]
then
    echo "-- Variables de entorno"
    export $(grep -v '^#' .env | xargs)
    # source .env && export $(sed '/^#/d' .env | cut -d= -f1)
    echo "   DB_HOST: ${DB_HOST}"
    echo "   DB_PORT: ${DB_PORT}"
    echo "   DB_NAME: ${DB_NAME}"
    echo "   DB_USER: ${DB_USER}"
    echo "   DB_PASS: ${DB_PASS}"
    echo "   ORIGINS: ${ORIGINS}"
    echo "   SALT: ${SALT}"
    echo
    export PGHOST=$DB_HOST
    export PGPORT=$DB_PORT
    export PGDATABASE=$DB_NAME
    export PGUSER=$DB_USER
    export PGPASSWORD=$DB_PASS
fi

if [ -d .venv ]
then
    echo "-- Python Virtual Environment"
    source .venv/bin/activate
    echo "   $(python3 --version)"
    export PYTHONPATH=$(pwd)
    echo "   PYTHONPATH: ${PYTHONPATH}"
    echo
    echo "-- Poetry"
    export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
    echo "   $(poetry --version)"
    echo
    echo "-- FastAPI 127.0.0.1:8000"
    alias arrancar="uvicorn --host=127.0.0.1 --port 8000 --reload pjecz_hercules_api_key.app:app"
    echo "   arrancar"
    echo
    if [ -d tests ]
    then
        echo "-- Pruebas unitarias"
        echo "   python3 -m unittest discover"
        echo
    fi
fi
```

## Arrancar

Cargar las variables de entorno y el entorno virtual

```bash
source .bashrc
```

Lanzar **FastAPI** por medio del _alias_ que se cargó en el `source .bashrc`

```bash
arrancar
```
