# SPEC 02 — Endpoint visualizar para entregar PDF desde Google Cloud Storage

> **Estado:** Implementado
> **Depende de:** —
> **Fecha:** 2026-10-21
> **Objetivo:** Agregar el endpoint `GET /visualizar/{id}` a edictos, glosas, listas de acuerdos y sentencias para entregar en línea el PDF guardado en Google Cloud Storage mediante `StreamingResponse`.

---

## Alcance

**Dentro:**

- Crear `src/pjecz_hercules_api_key/core/google_cloud_storage.py` con las funciones compartidas para obtener el `blob_name` y descargar el archivo.
- Agregar el endpoint `GET /visualizar/{id}` en los routers `edictos`, `glosas`, `listas_de_acuerdos` y `sentencias`.
- El `id` es parámetro de ruta, obligatorio y de tipo `int`.
- Revisar el permiso `Permiso.VER` del módulo correspondiente, igual que el endpoint paginado.
- Validar que el registro exista, que tenga `estatus == "A"` y que `url` no sea texto vacío.
- Obtener el `blob_name` a partir de `url` quitando el prefijo `/<bucket>/` de la ruta.
- Crear el cliente con `google.cloud.storage.Client()`, revisar que el blob exista y cargar su contenido en memoria.
- Entregar el contenido con `fastapi.responses.StreamingResponse`, `media_type="application/pdf"` y `Content-Disposition: inline`.
- Nombre de entrega con el formato `<prefijo>-<AUTORIDAD CLAVE>-<AAAA-MM-DD>.pdf`.

**Fuera de alcance (para specs futuras):**

- Modificar `tests/`. La verificación es manual desde `/docs` o con `curl`.
- Entrega de archivos PDF de oficios (`ofi_documentos` y `ofi_documentos_adjuntos`, bucket `GCP_BUCKET_OFICIOS`). Irá en una spec futura.
- Otras tablas con archivos (`exh_exhortos_archivos`, `redams`, etc.).
- Endpoint de descarga (`attachment`) o de detalle JSON (`GET /{id}`).
- Streaming por fragmentos directo desde GCS (`blob.open()`); el archivo se carga completo en memoria.
- Caché del contenido o de URLs firmadas.
- Cambios en modelos, esquemas o `main.py`.
- Nuevas variables en `config/setttings.py`; las de bucket ya existen.

---

## Modelo de datos

Esta funcionalidad no introduce tablas ni esquemas nuevos. Reutiliza las columnas `url`, `fecha`, `estatus` y la propiedad `autoridad_clave` de los modelos existentes, y las variables `GCP_BUCKET_*` de `config/setttings.py`.

### Tabla de endpoints

| Router | Ruta | Módulo de permiso | Variable del bucket | Prefijo del nombre |
| --- | --- | --- | --- | --- |
| `edictos` | `GET /edictos/visualizar/{id}` | `EDICTOS` | `GCP_BUCKET_EDICTOS` | `edicto` |
| `glosas` | `GET /glosas/visualizar/{id}` | `GLOSAS` | `GCP_BUCKET_GLOSAS` | `glosa` |
| `listas_de_acuerdos` | `GET /listas_de_acuerdos/visualizar/{id}` | `LISTAS DE ACUERDOS` | `GCP_BUCKET_LISTAS_DE_ACUERDOS` | `lista-de-acuerdos` |
| `sentencias` | `GET /sentencias/visualizar/{id}` | `SENTENCIAS` | `GCP_BUCKET_SENTENCIAS` | `sentencia` |

Ejemplo de nombre: `lista-de-acuerdos-SLT-J1-CIV-2025-01-15.pdf`, donde `fecha` es la columna `fecha` del registro en formato `AAAA-MM-DD`.

### Funciones de `core/google_cloud_storage.py`

| Función | Entrada | Salida | Regla |
| --- | --- | --- | --- |
| `get_blob_name_from_url(bucket_name, url)` | `str`, `str` | `str` | `urlparse(url).path`, debe iniciar con `/<bucket_name>/`; se quita ese prefijo y se aplica `unquote`. Si no coincide o queda vacío, 404. |
| `get_file_from_gcs(bucket_name, blob_name)` | `str`, `str` | `bytes` | Crea `storage.Client()`, obtiene `bucket.blob(blob_name)`; si `blob.exists()` es falso, 404; si no, regresa `blob.download_as_bytes()`. |

Ejemplo de `get_blob_name_from_url`:

```text
bucket_name = "pjecz-listas-de-acuerdos"
url = "https://storage.googleapis.com/pjecz-listas-de-acuerdos/listas_de_acuerdos/2025/01/15/archivo%20uno.pdf"
blob_name -> "listas_de_acuerdos/2025/01/15/archivo uno.pdf"
```

### Respuestas HTTP

| Caso | Código | `detail` |
| --- | --- | --- |
| Sin permiso `VER` en el módulo | 403 | `Forbidden` |
| `id` no es entero | 422 | (lo genera FastAPI) |
| El registro no existe | 404 | `Not found` |
| El registro tiene `estatus != "A"` | 404 | `Not found` |
| `url` es texto vacío (tras `strip`) | 404 | `File URL is empty` |
| `url` no corresponde al bucket configurado | 404 | `File URL is not valid` |
| El blob no existe en el bucket | 404 | `File not found in storage` |
| La variable `GCP_BUCKET_*` está vacía | 500 | `Missing bucket configuration` |
| Google Cloud Storage lanza `google.api_core.exceptions.GoogleAPIError` | 503 | `Storage service unavailable` |
| Éxito | 200 | Cuerpo PDF |

Convenciones:

- Las funciones lanzan `HTTPException` directamente, igual que `core/validation.py`, porque no se registra manejador de excepciones en `main.py`.
- Encabezados de éxito: `Content-Type: application/pdf` y `Content-Disposition: inline; filename="<nombre>"`.
- El cuerpo se entrega con `StreamingResponse(io.BytesIO(contenido), media_type="application/pdf", headers=...)`.

---

## Plan de implementación

Cada paso deja la API funcionando y se puede hacer commit de él por separado.

1. Crear `core/google_cloud_storage.py` con `get_blob_name_from_url` y `get_file_from_gcs`. Ningún router lo usa todavía. Prueba manual: en `python -c`, `get_blob_name_from_url("b", "https://storage.googleapis.com/b/x/y%20z.pdf")` regresa `"x/y z.pdf"`.
2. Agregar `GET /visualizar/{id}` en `routers/listas_de_acuerdos.py`. Prueba manual: `curl -H "X-Api-Key: ..." .../listas_de_acuerdos/visualizar/<id> -o salida.pdf` produce un PDF válido.
3. Agregar `GET /visualizar/{id}` en `routers/edictos.py`.
4. Agregar `GET /visualizar/{id}` en `routers/glosas.py`.
5. Agregar `GET /visualizar/{id}` en `routers/sentencias.py`.

---

## Criterios de aceptación

- [x] Existe `src/pjecz_hercules_api_key/core/google_cloud_storage.py` con `get_blob_name_from_url` y `get_file_from_gcs`.
- [x] `get_blob_name_from_url("b", "https://storage.googleapis.com/b/x/y%20z.pdf")` regresa `"x/y z.pdf"`.
- [x] `get_blob_name_from_url("b", "https://storage.googleapis.com/otro/x.pdf")` lanza `HTTPException` con 404.
- [x] Solo cambiaron los 4 routers de la tabla y el nuevo `core/google_cloud_storage.py` (`git diff --stat` lo confirma).
- [x] `/docs` muestra `GET /visualizar/{id}` en `edictos`, `glosas`, `listas_de_acuerdos` y `sentencias`, con `id` obligatorio.
- [x] Para un `id` existente con archivo, cada endpoint responde 200 con `Content-Type: application/pdf`.
- [x] El encabezado `Content-Disposition` es `inline; filename="lista-de-acuerdos-<AUTORIDAD CLAVE>-<AAAA-MM-DD>.pdf"` (y equivalente con `edicto`, `glosa`, `sentencia`).
- [x] El cuerpo descargado abre como PDF y es idéntico al blob en el bucket (mismo tamaño en bytes).
- [x] `GET /listas_de_acuerdos/visualizar/999999999` responde 404.
- [x] `GET /listas_de_acuerdos/visualizar/abc` responde 422.
- [x] Un registro con `estatus == "B"` responde 404.
- [x] Un registro con `url == ""` responde 404 con `detail == "File URL is empty"`.
- [x] Un registro cuyo blob no existe responde 404 con `detail == "File not found in storage"`.
- [x] Un usuario sin permiso `VER` en el módulo responde 403.
- [x] Los endpoints paginados `GET ""` de los 4 routers responden igual que antes de esta spec.

---

## Decisiones

- **Sí:** ruta `GET /visualizar/{id}`. Conserva la compatibilidad con la forma de ruta que ya usan los clientes; el `id` en la ruta es obligatorio por naturaleza.
- **No:** `GET /{id}/visualizar`. Se descartó para no romper la compatibilidad.
- **No:** `GET /visualizar?id=`.
- **Sí:** `blob_name` = ruta de la URL sin el prefijo `/<bucket>/`, con `unquote`. Verifica que la URL apunte al bucket configurado.
- **No:** usar el path completo sin verificar el bucket. Podría pedir un blob de otro bucket o con ruta incorrecta.
- **Sí:** `Content-Disposition: inline`. El endpoint se llama "visualizar"; el navegador muestra el PDF.
- **No:** `attachment`. Una descarga forzada iría en otra spec.
- **Sí:** lógica compartida en `core/google_cloud_storage.py`. Los 4 routers solo consultan el registro y arman el nombre.
- **No:** duplicar la lógica de GCS en cada router.
- **Sí:** nombre `<prefijo>-<AUTORIDAD CLAVE>-<AAAA-MM-DD>.pdf` en las 4 tablas. Es simple y consistente.
- **No:** agregar expediente o `id` al nombre. Se aceptan nombres repetidos entre registros del mismo día y autoridad.
- **Sí:** 404 cuando el registro no existe, está eliminado, no tiene `url` o el blob no existe. Para el cliente, en todos los casos no hay archivo que ver.
- **No:** 422 para `url` vacía.
- **Sí:** 500 si falta la variable del bucket y 503 si Google Cloud Storage falla. Se distingue un error de configuración de una falla del servicio.
- **Sí:** cargar todo el archivo en memoria con `download_as_bytes()` y entregarlo con `StreamingResponse` sobre `BytesIO`. Así lo pidió el usuario y permite responder 404 antes de empezar a enviar.
- **No:** streaming por fragmentos directo desde GCS.
- **Sí:** crear `storage.Client()` en cada petición, con las credenciales por defecto del entorno (App Engine).
- **No:** tests automatizados. Igual que SPEC 01, la verificación es manual.

---

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| PDFs muy grandes consumen memoria de la instancia `F2` de App Engine. | Se acepta; los documentos judiciales suelen ser de pocos MB. Si se vuelve problema, una spec futura cambia a streaming por fragmentos. |
| Hay URLs históricas con otro dominio o formato (p. ej. `storage.cloud.google.com` o sin el bucket en la ruta). | Responden 404 `File URL is not valid`. Antes del paso 2, revisar una muestra de `url` en cada tabla; si hay otros formatos, ajustar `get_blob_name_from_url`. |
| `autoridad_clave` puede tener caracteres no válidos en un nombre de archivo. | Las claves cumplen `^[A-Z0-9_-]+$` (ver `safe_clave` en SPEC 01), así que son seguras para el nombre. |
| Crear `storage.Client()` en cada petición añade latencia. | Se acepta por simplicidad; se puede cachear con `lru_cache` en una spec futura. |
| La cuenta de servicio de App Engine no tiene permiso de lectura en algún bucket. | Google lanza `Forbidden` (subclase de `GoogleAPIError`) y se responde 503; revisar IAM del bucket. |

---

## Lo que **no** está en esta spec

- Tests automatizados en `tests/`.
- Entrega de archivos PDF de oficios (spec futura).
- Otras tablas con archivos (exhortos, redams).
- Descarga forzada (`attachment`) o detalle JSON.
- Streaming por fragmentos o caché.
- Cambios en modelos, esquemas, `main.py` o `config/setttings.py`.

Cada uno de estos, si se hace, va en su propia spec.
