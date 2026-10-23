# pjecz-hercules-api-key

API de uso público para consultar edictos, listas de acuerdos, sentencias, etc.

## Objetivo

El objetivo de este proyecto es proporcionar datos abiertos e información pública sobre los procesos judiciales del Poder Judicial del Estado de Coahuila de Zaragoza.

## Descripción

El proyecto `pjecz-hercules-api-key` es una interfaz de acceso a una base de datos de edictos, listas de acuerdos, sentencias y otros documentos judiciales.

## Requerimientos

Los requerimientos son

- Python 3.14
- PostgreSQL 18
- Gestor de paquetes **uv**

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
pip install --upgrade pip
```

Instalar las dependencias

```bash
uv sync
```

## Configuración

Copiar el archivo `.env.example` a `.env` y modificar los valores según sea necesario.

```bash
cp .env.example .env
```

Crear un archivo `.bashrc` para cargar las variables de entorno y el entorno virtual

```bash
# pjecz-hercules-api-key

if [ -f ~/.bashrc ]
then
    . ~/.bashrc
fi

if command -v figlet &> /dev/null
then
    figlet Hercules API-key
else
    echo "== Hercules API-key"
fi
echo

export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.google-application-credentials/service-account.json
if [ -f $GOOGLE_APPLICATION_CREDENTIALS ]
then
    echo "-- Google Application Credentials"
    echo "   ${GOOGLE_APPLICATION_CREDENTIALS}"
    echo
fi

if [ -f .env ]
then
    export $(grep -v '^#' .env | xargs)
    echo "-- Variables de entorno"
    echo "   DB_HOST: ${DB_HOST}"
    echo "   DB_PORT: ${DB_PORT}"
    echo "   DB_NAME: ${DB_NAME}"
    echo "   DB_USER: ${DB_USER}"
    echo "   DB_PASS: ${DB_PASS}"
    echo "   SALT: ${SALT}"
    echo "   SQLALCHEMY_DATABASE_URI: ${SQLALCHEMY_DATABASE_URI}"
    echo "   TZ: ${TZ}"
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
    alias arrancar="uv run uvicorn pjecz_hercules_api_key.main:app"
    echo "-- Arrancar FasAPI"
    echo "   arrancar"
    echo
fi
```

## Uso

Cargar las variables de entorno y el entorno virtual

```bash
source .bashrc
```

Lanzar **FastAPI** por medio del _alias_ que se cargó en el `source .bashrc`

```bash
arrancar
```

## Licencia

GNU Affero General Public License v3.0

## Contacto

Si tienes alguna pregunta o problema, no dudes en contactarnos a través de nuestro correo electrónico o nuestro sitio web.
