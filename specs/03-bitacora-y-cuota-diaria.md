# SPEC 03 — Bitácora de operaciones y cuota diaria por usuario

> **Estado:** Implementado
> **Depende de:** —
> **Fecha:** 2026-10-21
> **Objetivo:** Registrar en la tabla `bitacoras_apis` cada petición de un usuario identificado (tiempo, usuario, ruta, petición y éxito o fallo) y usar ese registro para imponer una cuota diaria de consultas por usuario.

---

## Por qué existe esta spec

Hoy la API no deja rastro de quién la usa. La bitácora sirve para dos cosas:

1. **Cuota diaria por usuario**, que se impone aquí, en la API.
2. **Detectar API-keys sin uso en el último mes y borrarlas.** Ese mantenimiento se hará en `pjecz-hercules-cli-typer` leyendo la bitácora; esta spec solo garantiza que los datos existan.

El esquema de la base de datos lo define `pjecz-hercules-flask`. Este proyecto no crea ni migra tablas, así que los cambios de esquema se aplican allá y en la BD antes de desplegar.

---

## Alcance

**Dentro:**

- Crear el modelo `BitacoraAPI` en `src/pjecz_hercules_api_key/models/bitacoras_apis.py`, idéntico al de `pjecz-hercules-flask/hercules/blueprints/bitacoras_apis/models.py`, y registrarlo en `models/__init__.py`.
- Agregar a `Usuario` la columna `api_key_cuota_diaria` y el hijo `bitacoras_apis`.
- Agregar `API_NOMBRE` y `API_KEY_CUOTA_DIARIA` a `config/setttings.py` y `.env.example`.
- Agregar `api_key_cuota_diaria: int` a `UsuarioInDB` en `schemas/usuarios.py`.
- En `core/authentication.py`: marcar `request.state.usuario_id` en cuanto se identifica al usuario, contar sus peticiones del día y responder 429 al alcanzar la cuota.
- Crear `core/bitacora.py` con `guardar_bitacora()`.
- Agregar en `main.py` el middleware HTTP `registrar_bitacora`.
- Documentar el SQL y los cambios que requiere `pjecz-hercules-flask`.

**Fuera de alcance (para specs futuras):**

- Modificar `tests/`. La verificación es manual con `curl` y consultas SQL.
- Comandos de mantenimiento en `pjecz-hercules-cli-typer` (consultar la bitácora, eliminar API-keys sin uso, depurar registros viejos).
- Leer o escribir `usuarios.api_key_creado` desde esta API.
- Endpoint para que el usuario consulte su consumo o su cuota restante.
- Encabezados de cuota (`X-RateLimit-*`).
- Registrar peticiones cuya api_key no identifica a ningún usuario.

---

## Modelo de datos

### Tabla `bitacoras_apis` (existente)

Se reutiliza tal como está en `pjecz-hercules-flask`. `creado`, `modificado` y `estatus` vienen de `Base`.

| Dato pedido | Columna | Valor que escribe esta API |
| --- | --- | --- |
| Tiempo | `creado` | `now()` del servidor (`server_default`) |
| Usuario | `usuario_id` | `request.state.usuario_id` |
| Ruta | `api_ruta` | `request.url.path` + `?` + `request.url.query` si hay query; truncado a 512 |
| Petición | `peticion` | `request.method` (hoy siempre `"GET"`) |
| Éxito/fallo | `respuesta_exitosa` | `status_code < 400` |
| — | `api_nombre` | `settings.API_NOMBRE` |
| — | `respuesta_mensaje` | `"<código> <frase>"`, p. ej. `"429 Too Many Requests"` |
| — | `respuesta_errores` | `[]` (JSON NOT NULL) |
| — | `respuesta_datos` | `[]` (JSON NOT NULL) |

### Columna nueva en `usuarios`

| Columna | Tipo | Regla |
| --- | --- | --- |
| `api_key_cuota_diaria` | `INTEGER NULL` | Si es nula o 0, se usa `settings.API_KEY_CUOTA_DIARIA`. |

### Variables de configuración

| Variable | Tipo | Valor por defecto |
| --- | --- | --- |
| `API_NOMBRE` | `str` | `"pjecz-hercules-api-key"` |
| `API_KEY_CUOTA_DIARIA` | `int` | `1000` |

### Funciones nuevas

| Función | Archivo | Regla |
| --- | --- | --- |
| `count_today_requests(usuario_id, session)` | `core/authentication.py` | `count(*)` de `bitacoras_apis` con ese `usuario_id`, `api_nombre == settings.API_NOMBRE` y `creado >= date_trunc('day', now() AT TIME ZONE settings.TZ) AT TIME ZONE settings.TZ` (medianoche local, comparable con `creado` aunque PostgreSQL esté en UTC). |
| `guardar_bitacora(usuario_id, ruta, peticion, status_code)` | `core/bitacora.py` | Inserta con `session_scope()`; cualquier excepción se registra con `logging` y no se propaga. |
| `registrar_bitacora(request, call_next)` | `main.py` | Middleware `http`. Si `call_next` lanza una excepción, el código es 500. En `finally`, si existe `request.state.usuario_id`, llama `await run_in_threadpool(guardar_bitacora, ...)`. |

### Respuestas HTTP

| Caso | Código | `detail` | ¿Se registra? |
| --- | --- | --- | --- |
| api_key con formato inválido, ID no descifrable o usuario inexistente | 403 | Mensaje de `MyAuthenticationError` | No |
| Usuario identificado con api_key distinta, email no coincide, expirada o inactivo | 403 | Mensaje de `MyAuthenticationError` | Sí, `respuesta_exitosa = false` |
| Peticiones del día `>=` cuota | 429 | `Ha excedido su cuota diaria de consultas` | Sí, `respuesta_exitosa = false` |
| Sin permiso en el módulo | 403 | `Forbidden` | Sí, `respuesta_exitosa = false` |
| Excepción no manejada | 500 | — | Sí, `respuesta_exitosa = false` |
| Éxito (JSON o PDF de SPEC 02) | 200 | — | Sí, `respuesta_exitosa = true` |

### Cambios requeridos fuera de este proyecto

En `pjecz-hercules-flask`:

1. `usuarios/models.py`: agregar `api_key_cuota_diaria: Mapped[Optional[int]]`.
2. `usuarios/models.py`: agregar `api_key_creado: Mapped[Optional[datetime]]` y llenarlo al generar la api_key. Lo usará el CLI para no borrar keys recién emitidas.
3. `bitacoras_apis/models.py`: agregar `Index("bitacoras_apis_usuario_id_creado_idx", "usuario_id", "creado")` en `__table_args__`.

SQL para la base de datos existente:

```sql
ALTER TABLE usuarios ADD COLUMN api_key_cuota_diaria INTEGER;
ALTER TABLE usuarios ADD COLUMN api_key_creado TIMESTAMP;
CREATE INDEX bitacoras_apis_usuario_id_creado_idx ON bitacoras_apis (usuario_id, creado);
```

---

## Plan de implementación

Cada paso deja la API funcionando, siempre que el SQL ya esté aplicado en la BD.

1. Aplicar el SQL en la base de datos de desarrollo.
2. Crear `models/bitacoras_apis.py`, registrarlo en `models/__init__.py` y agregar `api_key_cuota_diaria` y `bitacoras_apis` a `models/usuarios.py`. Prueba: `configure_mappers()` no lanza error.
3. Agregar `API_NOMBRE` y `API_KEY_CUOTA_DIARIA` a `config/setttings.py` y `.env.example`; agregar `api_key_cuota_diaria` a `UsuarioInDB` y llenarlo en `get_user`.
4. Crear `core/bitacora.py` con `guardar_bitacora()`.
5. En `core/authentication.py`: `authenticate_user` recibe `request` opcional y marca `request.state.usuario_id`; `get_current_active_user` recibe `request: Request`, pasa el `request` y valida la cuota con `count_today_requests`.
6. Agregar el middleware `registrar_bitacora` en `main.py`. Prueba: `curl` a un endpoint y ver la fila nueva en `bitacoras_apis`.

---

## Criterios de aceptación

- [x] El SQL de esta spec está aplicado en la base de datos.
- [x] Existe `src/pjecz_hercules_api_key/models/bitacoras_apis.py` y `BitacoraAPI` está en `models/__init__.py`.
- [x] `GET /estados` con api_key válida responde 200 y crea una fila con `usuario_id` correcto, `api_nombre = 'pjecz-hercules-api-key'`, `api_ruta = '/estados'`, `peticion = 'GET'`, `respuesta_exitosa = true` y `respuesta_mensaje = '200 OK'`.
- [x] `GET /estados?clave=05` guarda `api_ruta = '/estados?clave=05'`.
- [x] Una petición a un módulo sin permiso responde 403 y crea una fila con `respuesta_exitosa = false` y `respuesta_mensaje = '403 Forbidden'`.
- [x] Una api_key expirada de un usuario existente responde 403 y crea una fila con `respuesta_exitosa = false`.
- [x] Una api_key con formato inválido responde 403 y no crea ninguna fila.
- [x] Con `api_key_cuota_diaria = 3` y sin filas del día, las peticiones 1 a 3 pasan la validación de cuota y la cuarta responde 429 con `detail = 'Ha excedido su cuota diaria de consultas'`.
- [x] La petición rechazada con 429 también queda registrada.
- [x] Con PostgreSQL en `Etc/UTC`, el límite inferior del conteo es la medianoche de `America/Mexico_City` (06:00 UTC), no la medianoche UTC.
- [x] Con `api_key_cuota_diaria` nula, la cuota aplicada es `API_KEY_CUOTA_DIARIA` (1000 por defecto).
- [x] `GET /edictos/visualizar/{id}` entrega el PDF igual que en SPEC 02 y queda registrado con 200.
- [x] Si la inserción en `bitacoras_apis` falla, la respuesta al cliente no cambia y el error aparece en el log.
- [x] Los endpoints paginados responden igual que antes de esta spec para usuarios bajo su cuota.

---

## Decisiones

- **Sí:** reutilizar la tabla `bitacoras_apis` de `pjecz-hercules-flask`. Ya existe en el esquema y tiene vista en el Flask.
- **No:** una tabla nueva. Duplicaría el concepto.
- **Sí:** `api_nombre = settings.API_NOMBRE`. Distingue esta API de otras que escriban en la misma tabla, y el conteo de cuota filtra por ella.
- **Sí:** cuota por usuario en `usuarios.api_key_cuota_diaria`, con valor por defecto en settings cuando es nula.
- **No:** solo una cuota global en settings. No permite dar más cuota a integraciones específicas.
- **Sí:** cuentan todas las peticiones, exitosas y fallidas. Evita el abuso con peticiones que fallan.
- **No:** contar solo las exitosas.
- **Sí:** registrar con un middleware HTTP. Ve el código de estado final de cualquier router sin modificar los 44 routers.
- **No:** registrar dentro de cada endpoint o en la dependencia. La dependencia corre antes de conocer el resultado.
- **Sí:** identificar al usuario con `request.state.usuario_id`, puesto en `authenticate_user` en cuanto el usuario existe. Así también se registran los rechazos por expiración o inactividad.
- **No:** registrar peticiones sin usuario identificado. `usuario_id` es NOT NULL.
- **Sí:** escribir con `run_in_threadpool` y una sesión propia (`session_scope()`). La sesión de la dependencia ya está cerrada y no se bloquea el event loop.
- **Sí:** si falla la escritura de la bitácora, solo se registra en el log. La bitácora no debe tumbar la API.
- **Sí:** el día de la cuota empieza a la medianoche de `settings.TZ`, calculada en PostgreSQL con `date_trunc('day', now() AT TIME ZONE TZ) AT TIME ZONE TZ`. Usa el índice `(usuario_id, creado)`.
- **No:** `date_trunc('day', now())`. En la verificación PostgreSQL resultó estar en `Etc/UTC` y la cuota se reiniciaba a las 18:00 de Coahuila.
- **Sí:** `respuesta_errores` y `respuesta_datos` se guardan como `[]`. Son NOT NULL y no se quiere guardar el contenido de las respuestas.
- **Sí:** `api_key_creado` se documenta como requisito de esquema, pero esta API no la usa; la consumirá el CLI.
- **No:** tests automatizados. Igual que SPEC 01 y 02, la verificación es manual.

---

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Desplegar antes de aplicar el SQL: `usuarios.api_key_cuota_diaria` no existe y todas las peticiones fallan. | Aplicar el SQL en producción antes del despliegue. |
| La zona horaria de PostgreSQL no es `America/Mexico_City` (en desarrollo es `Etc/UTC`). | El límite del día se calcula explícitamente con `settings.TZ`. Esto supone que `creado` se guarda en la zona de la sesión de PostgreSQL, que es lo que hace `now()`. |
| La tabla crece con cada petición. | El CLI tendrá un comando para depurar registros viejos (spec futura en `pjecz-hercules-cli-typer`). |
| Dos peticiones simultáneas pueden pasar la cuota por una o dos consultas. | Se acepta; la cuota es un límite de uso razonable, no de facturación. |
| Una falla en la consulta de conteo responde 500. | Se acepta; si la BD no responde, los endpoints tampoco podrían funcionar. |

---

## Lo que **no** está en esta spec

- Tests automatizados en `tests/`.
- Comandos de mantenimiento en `pjecz-hercules-cli-typer`.
- Uso de `api_key_creado` desde esta API.
- Endpoint de consumo o encabezados `X-RateLimit-*`.
- Registro de peticiones sin usuario identificado.

Cada uno de estos, si se hace, va en su propia spec.
