# SPEC 04 — Configuración desde Google Cloud Secret Manager

> **Estado:** Aprobado
> **Depende de:** —
> **Fecha:** 2026-10-21
> **Objetivo:** Hacer que `Settings` lea cada propiedad primero de Google Cloud Secret Manager cuando `PROJECT_ID` está definido, después de las variables de entorno y al final de su valor por defecto.

---

## Por qué existe esta spec

En App Engine no hay archivo `.env` y no conviene poner contraseñas ni el `SALT` en `app.yaml`. Los secretos ya viven en Secret Manager con el prefijo `pjecz_plataforma_web_api_key`. Fuera de Google Cloud (desarrollo local) todo debe seguir funcionando igual que hoy con `.env` y variables de entorno.

---

## Alcance

**Dentro:**

- Crear la clase `SecretManagerSettingsSource` (subclase de `pydantic_settings.PydanticBaseSettingsSource`) en `src/pjecz_hercules_api_key/config/setttings.py`.
- Registrar esa fuente en `Settings.settings_customise_sources` con prioridad sobre las variables de entorno y `.env`.
- Buscar en Secret Manager **todas** las propiedades de `Settings`.
- Detectar Google Cloud por la variable de entorno `PROJECT_ID`.
- Formar el nombre del secreto como `f"{SERVICE_PREFIX}_{CAMPO}".lower()` y leer la versión `latest`.
- Documentar `PROJECT_ID` y `SERVICE_PREFIX` en `.env.example` (comentadas).

**Fuera de alcance (para specs futuras):**

- Modificar `tests/`. La verificación es manual.
- Cambiar `app.yaml`. El prefijo `pjecz_plataforma_web_api_key` se queda como está.
- Crear los secretos o los permisos IAM desde código. Es una tarea operativa previa al despliegue.
- Recargar secretos sin reiniciar la instancia (`get_settings()` sigue con `lru_cache`).
- Leer versiones específicas de un secreto distintas de `latest`.
- Cambiar los nombres o tipos de las propiedades existentes de `Settings`.

---

## Modelo de datos

Esta funcionalidad no agrega propiedades a `Settings`. `PROJECT_ID` y `SERVICE_PREFIX` se leen con `os.environ` dentro de la fuente; no son campos de `Settings`.

### Orden de resolución por propiedad

| Prioridad | Fuente | Cuándo aplica |
| --- | --- | --- |
| 1 | Argumentos de `Settings(...)` (`init_settings`) | Siempre (hoy nadie los usa). |
| 2 | `SecretManagerSettingsSource` | Solo si `PROJECT_ID` está definido y el secreto existe. |
| 3 | Variables de entorno (`env_settings`) | Siempre. |
| 4 | Archivo `.env` (`dotenv_settings`) | Siempre. |
| 5 | `file_secret_settings` | Se conserva por compatibilidad con pydantic-settings. |
| 6 | Valor por defecto de la propiedad | Si ninguna fuente lo dio. |

`settings_customise_sources` regresa la tupla en ese orden:

```python
(init_settings, SecretManagerSettingsSource(settings_cls), env_settings, dotenv_settings, file_secret_settings)
```

### Nombre del secreto

```text
SERVICE_PREFIX = "pjecz_plataforma_web_api_key"
campo          = "DB_PASS"
secreto        = "pjecz_plataforma_web_api_key_db_pass"
ruta           = "projects/{PROJECT_ID}/secrets/pjecz_plataforma_web_api_key_db_pass/versions/latest"
```

### Comportamiento de `SecretManagerSettingsSource.__call__()`

| Caso | Resultado |
| --- | --- |
| `PROJECT_ID` no definido o vacío | Regresa `{}`. No importa ni crea el cliente de Secret Manager. |
| `PROJECT_ID` definido y `SERVICE_PREFIX` no definido o vacío | Lanza `ValueError("SERVICE_PREFIX is required when PROJECT_ID is set")`. La app no arranca. |
| El secreto existe | Agrega `{campo: valor}` con `payload.data.decode("utf-8").strip()`. |
| El secreto no existe (`google.api_core.exceptions.NotFound`) | Omite el campo; lo resuelven las fuentes siguientes. |
| Cualquier otra excepción (permisos, red, cuota) | Se propaga. La app no arranca. |

Convenciones:

- Se crea **un solo** `secretmanager.SecretManagerServiceClient()` por llamada a `__call__()`, reutilizado para todos los campos.
- El import de `google.cloud.secretmanager` se hace dentro de la rama de `PROJECT_ID` para no cargarlo en desarrollo local.
- Los valores se entregan como `str`; pydantic hace la conversión de tipos (`int` para `DB_PORT` y `API_KEY_CUOTA_DIARIA`).
- `get_field_value()` (abstracto en la clase base) se implementa, pero `__call__()` es quien arma el diccionario completo.

---

## Plan de implementación

Cada paso deja la API funcionando y se puede hacer commit de él por separado.

1. Crear `SecretManagerSettingsSource` en `config/setttings.py`, sin registrarla todavía. Prueba manual: con `PROJECT_ID` sin definir, `python -c "from pjecz_hercules_api_key.config.setttings import Settings, SecretManagerSettingsSource; print(SecretManagerSettingsSource(Settings)())"` imprime `{}`.
2. Agregar `settings_customise_sources` a `Settings` con el orden de la tabla. Prueba manual: sin `PROJECT_ID`, `get_settings()` da los mismos valores que antes (desde `.env` y variables de entorno) y `arrancar` levanta la API.
3. Agregar a `.env.example` un bloque comentado con `PROJECT_ID` y `SERVICE_PREFIX` que explique que solo se definen para leer de Secret Manager.
4. Verificar en Google Cloud (operativo): los secretos necesarios existen con el prefijo, la cuenta de servicio de App Engine tiene `roles/secretmanager.secretAccessor`, y se despliega con `gcloud app deploy`.

---

## Criterios de aceptación

- [ ] `config/setttings.py` contiene `SecretManagerSettingsSource` y `Settings.settings_customise_sources`.
- [ ] Sin `PROJECT_ID`, `SecretManagerSettingsSource(Settings)()` regresa `{}` y no crea `SecretManagerServiceClient`.
- [ ] Sin `PROJECT_ID`, `DB_NAME=x python -c "...get_settings().DB_NAME"` imprime `x`.
- [ ] Sin `PROJECT_ID` ni variable `TZ`, `get_settings().TZ` es `"America/Mexico_City"`.
- [ ] Con `PROJECT_ID` definido y `SERVICE_PREFIX` vacío, `Settings()` lanza `ValueError`.
- [ ] Con `PROJECT_ID` y `SERVICE_PREFIX` definidos y credenciales locales (`gcloud auth application-default login`), `Settings().DB_NAME` es el valor del secreto `pjecz_plataforma_web_api_key_db_name`, aunque exista `DB_NAME` en el entorno.
- [ ] En el mismo escenario, un campo sin secreto en GCP (p. ej. `GCP_BUCKET_OFICIOS`) toma el valor de la variable de entorno si existe, y si no, su valor por defecto.
- [ ] El secreto de `DB_PORT` se convierte a `int` (`type(Settings().DB_PORT) is int`).
- [ ] Un valor de secreto con salto de línea final (`"abc\n"`) se lee como `"abc"`.
- [ ] Con `PROJECT_ID` definido y credenciales sin permiso de lectura, `Settings()` lanza la excepción de Google (`PermissionDenied`) en vez de usar valores por defecto.
- [ ] Desplegada en App Engine, la API responde 200 en `GET /estados` con una api_key válida (conexión a BD y `SALT` vienen de Secret Manager).
- [ ] Solo cambiaron `config/setttings.py` y `.env.example` (`git diff --stat` lo confirma).

---

## Decisiones

- **Sí:** detectar Google Cloud por `PROJECT_ID`. Ya está en `app.yaml` y no existe en desarrollo local.
- **Sí:** nombre del secreto `f"{SERVICE_PREFIX}_{CAMPO}".lower()`. Así lo pidió el usuario y coincide con los secretos existentes.
- **Sí:** el prefijo `pjecz_plataforma_web_api_key` se mantiene. Los secretos en GCP ya usan ese nombre.
- **Sí:** buscar todas las propiedades de `Settings`. Es uniforme y no obliga a mantener una lista de campos sensibles.
- **No:** solo una lista fija de campos sensibles. Hay que recordar actualizarla cada que se agrega una propiedad.
- **Sí:** si un secreto no existe (`NotFound`), seguir con variables de entorno y luego el valor por defecto. Permite dejar valores no sensibles en `app.yaml` sin crear un secreto.
- **No:** ir directo al valor por defecto o fallar si falta un secreto.
- **Sí:** cualquier otro error de Secret Manager detiene el arranque. Evita que la API arranque con `SALT` o credenciales de BD vacías sin que nadie lo note.
- **No:** registrar el error en el log y continuar.
- **Sí:** `PROJECT_ID` sin `SERVICE_PREFIX` lanza `ValueError`. Es un error de despliegue; buscar sin prefijo podría leer secretos de otro servicio.
- **Sí:** fuente propia de pydantic-settings con `settings_customise_sources`. Es el mecanismo idiomático y pydantic sigue convirtiendo tipos.
- **No:** leer los secretos en `get_settings()` y pasarlos como argumentos a `Settings(...)`.
- **Sí:** versión `latest`. Rotar un secreto solo requiere agregar una versión y reiniciar.
- **Sí:** `.strip()` al valor del secreto. Los secretos creados con `echo ... | gcloud secrets create` suelen traer `\n` final, que rompería `SALT` o la contraseña.
- **Sí:** un solo cliente por construcción de `Settings`. `get_settings()` tiene `lru_cache`, así que es una vez por proceso.
- **No:** tests automatizados. Igual que SPEC 01 a 03, la verificación es manual.

---

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Cada proceso hace 16 llamadas a Secret Manager al arrancar (2 workers de gunicorn × hasta 4 instancias). | Se acepta; es solo al arrancar y el costo por acceso es mínimo. Si molesta, una spec futura usa `batch` o un solo secreto JSON. |
| La cuenta de servicio de App Engine no tiene `roles/secretmanager.secretAccessor`. | La app no arranca y el error aparece en los logs de App Engine. Revisar IAM antes del paso 4. |
| Un secreto obsoleto o mal escrito tiene prioridad sobre la variable de entorno. | Es el comportamiento pedido. Corregir el secreto con una nueva versión y reiniciar. |
| `strip()` elimina espacios que fueran parte intencional del valor. | Se acepta; ninguna propiedad actual depende de espacios al inicio o al final. |
| Con `PROJECT_ID` definido en local sin credenciales, `Settings()` falla. | Es el comportamiento esperado; en local no se define `PROJECT_ID` (queda comentado en `.env.example`). |

---

## Lo que **no** está en esta spec

- Tests automatizados en `tests/`.
- Cambios en `app.yaml`.
- Creación de secretos o permisos IAM desde código.
- Recarga de secretos sin reiniciar.
- Versiones de secreto distintas de `latest`.

Cada uno de estos, si se hace, va en su propia spec.
