# SPEC 08 — Límite de visualizaciones de PDF por hora

> **Estado:** Implementado
> **Depende de:** SPEC 02, SPEC 03
> **Fecha:** 2026-11-03
> **Objetivo:** Limitar a cada usuario a un número de visualizaciones de PDF (`GET /<tabla>/visualizar/{id}` de edictos, glosas, listas de acuerdos y sentencias) en los últimos 60 minutos, tomado de la nueva columna `usuarios.api_key_visualizaciones_por_hora` o, si no está definida, de `API_KEY_VISUALIZACIONES_POR_HORA` (20 por defecto).

---

## Por qué existe esta spec

Cada visualización (SPEC 02) descarga el PDF completo desde Google Cloud Storage y lo carga en la memoria de la instancia. Es mucho más costosa que una consulta JSON. La cuota diaria de SPEC 03 (1000 por defecto) no distingue entre ambas, así que un usuario podría bajar cientos de PDF en pocos minutos.

La bitácora de SPEC 03 ya registra cada petición con su ruta y su resultado. Este límite se calcula contando esas filas, sin tablas nuevas.

El esquema de la base de datos lo define `pjecz-hercules-flask`. La columna nueva se agrega allá y en la BD antes de desplegar.

---

## Alcance

**Dentro:**

- Agregar a `Usuario` (`models/usuarios.py`) la columna `api_key_visualizaciones_por_hora`.
- Agregar `api_key_visualizaciones_por_hora: int` a `UsuarioInDB` (`schemas/usuarios.py`) y llenarlo en `get_user` con el valor de la columna o, si es nula o 0, con `settings.API_KEY_VISUALIZACIONES_POR_HORA`.
- Agregar `API_KEY_VISUALIZACIONES_POR_HORA: int = 20` a `config/setttings.py` y `API_KEY_VISUALIZACIONES_POR_HORA=20` a `.env.example`.
- En `core/authentication.py`:
  - Crear `VISUALIZAR_RUTAS_PREFIJOS` con los 4 segmentos de ruta.
  - Crear `count_last_hour_views(usuario_id, session)`, que regresa el conteo y la fecha más vieja de las visualizaciones en la ventana.
  - Crear la dependencia `get_current_active_user_visualizar`, que reutiliza `get_current_active_user` (api_key y cuota diaria) y después valida el límite por hora.
- En los 4 endpoints `*_visualizar` cambiar `Depends(get_current_active_user)` por `Depends(get_current_active_user_visualizar)`.
- Al exceder el límite, responder 429 con `detail` propio y el encabezado `Retry-After`.
- Documentar el SQL y el cambio que requiere `pjecz-hercules-flask`.

**Fuera de alcance (para specs futuras):**

- Modificar `tests/`. La verificación es manual con `curl` y consultas SQL.
- Límite por hora para otros endpoints (paginados, detalle `GET /{id}`, oficios, exhortos).
- Límites separados por tipo de documento.
- Encabezados informativos (`X-RateLimit-Limit`, `X-RateLimit-Remaining`) en respuestas exitosas.
- Endpoint para que el usuario consulte su consumo o su límite.
- Caché de PDF para que las visualizaciones repetidas no descarguen de GCS.
- Cambios a `core/bitacora.py`, al middleware `registrar_bitacora` o a la tabla `bitacoras_apis`.
- Cambios a la cuota diaria de SPEC 03.

---

## Modelo de datos

### Columna nueva en `usuarios`

| Columna | Tipo | Regla |
| --- | --- | --- |
| `api_key_visualizaciones_por_hora` | `INTEGER NULL` | Si es nula o 0, se usa `settings.API_KEY_VISUALIZACIONES_POR_HORA`. |

En `models/usuarios.py`, junto a `api_key_cuota_diaria`:

```python
api_key_visualizaciones_por_hora: Mapped[Optional[int]]
```

### Variable de configuración

| Variable | Tipo | Valor por defecto |
| --- | --- | --- |
| `API_KEY_VISUALIZACIONES_POR_HORA` | `int` | `20` |

Como toda variable de `Settings`, también se puede definir en Secret Manager (SPEC 04).

### Rutas que cuentan

```python
VISUALIZAR_RUTAS_PREFIJOS = (
    "/edictos/visualizar/",
    "/glosas/visualizar/",
    "/listas_de_acuerdos/visualizar/",
    "/sentencias/visualizar/",
)
```

El límite es **uno combinado** para los 4 segmentos.

La app se crea con `FastAPI(root_path="/api/v5")` (`main.py`), así que la bitácora guarda rutas como `/api/v5/sentencias/visualizar/153226`. Por eso los segmentos se buscan **dentro** de `api_ruta` con `contains`, no al inicio con `startswith`. Así cuentan las filas con o sin `/api/v5`.

### Funciones nuevas en `core/authentication.py`

| Función | Regla |
| --- | --- |
| `count_last_hour_views(usuario_id, session)` | Una sola consulta a `bitacoras_apis` que regresa `(count(*), min(creado))`. Filtros: `usuario_id`, `api_nombre == settings.API_NOMBRE`, `creado >= now() - interval '1 hour'`, `or_(*[BitacoraAPI.api_ruta.contains(p, autoescape=True) for p in VISUALIZAR_RUTAS_PREFIJOS])` y `not_(BitacoraAPI.respuesta_mensaje.startswith("429"))`. |
| `get_current_active_user_visualizar(request, api_key, session)` | `async`. Llama `await get_current_active_user(request, api_key, session)`. Si `conteo >= usuario.api_key_visualizaciones_por_hora`, lanza `HTTPException` 429 con `headers={"Retry-After": "<segundos>"}`. Si no, regresa el usuario. |

Reglas del conteo:

- **Ventana deslizante:** últimos 60 minutos desde `now()` de PostgreSQL. No depende de `settings.TZ`.
- **Cuentan todas las respuestas** (200, 403, 404, 500, 503…) **excepto los 429**. Así un cliente que reintenta después del bloqueo no alarga su propio bloqueo.
- `autoescape=True` evita que el `_` de `listas_de_acuerdos` actúe como comodín de `LIKE`.
- La petición en curso todavía no está en la bitácora (el middleware la guarda al final). Con límite 20, las peticiones 1 a 20 pasan y la 21 responde 429.
- Se usa el índice existente `bitacoras_apis_usuario_id_creado_idx (usuario_id, creado)`.

Cálculo de `Retry-After`:

- `segundos = ceil((min(creado) + 1 hora) - now())`, calculado en PostgreSQL o en Python con la misma referencia de tiempo.
- Si el resultado es menor que 1, se usa `1`.
- Es el momento en que la visualización más vieja de la ventana sale de ella y se libera un lugar.

### Respuestas HTTP de `GET /<tabla>/visualizar/{id}`

Orden de las validaciones: api_key (403) → cuota diaria (429) → límite por hora (429) → permiso `VER` (403) → registro y archivo (404/500/503 de SPEC 02).

| Caso | Código | `detail` | Encabezado | ¿Cuenta para el límite por hora? |
| --- | --- | --- | --- | --- |
| api_key inválida, expirada o usuario inactivo | 403 | Mensaje de `MyAuthenticationError` | — | Sí, si el usuario fue identificado (SPEC 03) |
| Cuota diaria excedida | 429 | `Ha excedido su cuota diaria de consultas` | — | No |
| Visualizaciones de la última hora `>=` límite | 429 | `Ha excedido su límite de visualizaciones por hora` | `Retry-After: <segundos>` | No |
| Sin permiso `VER` | 403 | `Forbidden` | — | Sí |
| Registro inexistente, eliminado o sin archivo | 404 | Igual que SPEC 02 | — | Sí |
| Error de configuración o de GCS | 500 / 503 | Igual que SPEC 02 | — | Sí |
| Éxito | 200 | Cuerpo PDF | — | Sí |

Todas estas respuestas se siguen registrando en la bitácora y siguen contando para la cuota diaria, igual que en SPEC 03.

### Cambios requeridos fuera de este proyecto

En `pjecz-hercules-flask`, `usuarios/models.py`: agregar `api_key_visualizaciones_por_hora: Mapped[Optional[int]]`.

SQL para la base de datos existente:

```sql
ALTER TABLE usuarios ADD COLUMN api_key_visualizaciones_por_hora INTEGER;
```

---

## Plan de implementación

Cada paso deja la API funcionando, siempre que el SQL ya esté aplicado en la BD.

1. Aplicar el SQL en la base de datos de desarrollo.
2. Agregar `api_key_visualizaciones_por_hora` a `models/usuarios.py`. Agregar `API_KEY_VISUALIZACIONES_POR_HORA` a `config/setttings.py` y `.env.example`. Agregar el campo a `UsuarioInDB` y llenarlo en `get_user`. Prueba: `GET /estados` responde 200 igual que antes.
3. En `core/authentication.py`, crear `VISUALIZAR_RUTAS_PREFIJOS` y `count_last_hour_views`. Ningún endpoint la usa todavía. Prueba: en `python -c` con una sesión, el conteo coincide con un `SELECT` manual sobre `bitacoras_apis`.
4. En `core/authentication.py`, crear `get_current_active_user_visualizar` con el 429 y `Retry-After`.
5. Cambiar la dependencia en `routers/listas_de_acuerdos.py` (`listas_de_acuerdos_visualizar`). Prueba manual: con `api_key_visualizaciones_por_hora = 3`, la cuarta visualización responde 429.
6. Cambiar la dependencia en `routers/edictos.py`, `routers/glosas.py` y `routers/sentencias.py`.

---

## Criterios de aceptación

- [x] El SQL de esta spec está aplicado en la base de datos.
- [x] Con `api_key_visualizaciones_por_hora` nula, el límite aplicado es `API_KEY_VISUALIZACIONES_POR_HORA` (20 sin definir la variable).
- [x] Con `api_key_visualizaciones_por_hora = 0`, el límite aplicado también es `API_KEY_VISUALIZACIONES_POR_HORA`.
- [x] Con `API_KEY_VISUALIZACIONES_POR_HORA=5` en `.env` y la columna nula, la sexta visualización en una hora responde 429.
- [x] Con `api_key_visualizaciones_por_hora = 3` y sin visualizaciones en la última hora, las visualizaciones 1 a 3 responden 200 y la cuarta responde 429 con `detail = "Ha excedido su límite de visualizaciones por hora"`.
- [x] El 429 por límite de visualizaciones incluye el encabezado `Retry-After` con un entero entre 1 y 3600.
- [x] El límite es combinado: con límite 3, una visualización de edicto, una de glosa y una de sentencia hacen que la siguiente de lista de acuerdos responda 429.
- [x] Una visualización que responde 404 (p. ej. `id` inexistente) cuenta para el límite.
- [x] Las filas con `respuesta_mensaje` que empieza con `429` no cuentan: después de varios 429, el usuario vuelve a obtener 200 en cuanto la visualización más vieja cumple 60 minutos.
- [x] Una visualización de hace 61 minutos no cuenta para el límite.
- [x] Las filas de `/listas_de_acuerdos/...` que no son `/visualizar/` (p. ej. `/listas_de_acuerdos/123`, `/listas_de_acuerdos?autoridad_clave=X`) no cuentan.
- [x] Las filas de otro `api_nombre` no cuentan.
- [x] Un usuario que alcanzó el límite por hora sigue obteniendo 200 en `GET /edictos`, `GET /edictos/{id}` y demás endpoints que no son de visualización.
- [x] Un usuario sin permiso `VER` en `EDICTOS` y con el límite excedido recibe 429 (el límite se valida antes del permiso).
- [x] La petición rechazada con 429 por el límite queda registrada en `bitacoras_apis` con `respuesta_mensaje = '429 Too Many Requests'`.
- [x] Con la cuota diaria excedida, `GET /edictos/visualizar/{id}` responde 429 con `detail = "Ha excedido su cuota diaria de consultas"`, igual que antes de esta spec.
- [x] Solo cambiaron `models/usuarios.py`, `schemas/usuarios.py`, `config/setttings.py`, `.env.example`, `core/authentication.py` y los 4 routers `edictos`, `glosas`, `listas_de_acuerdos` y `sentencias` (`git diff --stat` lo confirma).

---

## Decisiones

- **Sí:** contar desde `bitacoras_apis`. Ya registra ruta, usuario y resultado de cada petición (SPEC 03) y tiene índice por `(usuario_id, creado)`.
- **No:** una tabla o contador nuevo (p. ej. en memoria o Redis). App Engine tiene varias instancias y la bitácora ya es la fuente de verdad.
- **Sí:** columna `usuarios.api_key_visualizaciones_por_hora` con valor por defecto en settings cuando es nula o 0. Mismo patrón y mismo criterio que `api_key_cuota_diaria`.
- **No:** 0 como "sin visualizaciones". Rompería la simetría con la cuota diaria.
- **Sí:** variable `API_KEY_VISUALIZACIONES_POR_HORA` con valor por defecto `20`.
- **Sí:** ventana deslizante de 60 minutos con `now() - interval '1 hour'`. Evita ráfagas de hasta el doble del límite al cambiar de hora.
- **No:** hora de reloj (`date_trunc('hour', ...)` en `settings.TZ`).
- **Sí:** un solo límite combinado para los 4 tipos de documento. El costo (descarga de PDF desde GCS) es el mismo en los 4.
- **No:** un límite por tipo. Requeriría 4 columnas o permitiría 4 veces el límite.
- **Sí:** cuentan todas las respuestas de visualización, exitosas o fallidas. Evita el abuso con `id` inválidos.
- **Sí:** excluir los 429 del conteo. Si contaran, un cliente que reintenta seguiría bloqueado indefinidamente.
- **No:** contar solo las exitosas.
- **Sí:** identificar las visualizaciones buscando el segmento dentro de `api_ruta` con `contains(..., autoescape=True)`. No requiere columnas nuevas en la bitácora y funciona con o sin el `root_path` `/api/v5`.
- **No:** `startswith` con los segmentos tal cual. Se descubrió en la implementación que la bitácora guarda la ruta con `/api/v5` y nunca coincidiría.
- **No:** `startswith(request.scope["root_path"] + segmento)`. Cambiaría la firma de `count_last_hour_views` y no contaría filas guardadas sin el prefijo.
- **No:** fijar `/api/v5` en `VISUALIZAR_RUTAS_PREFIJOS`. Se rompería en silencio al cambiar la versión del `root_path`.
- **No:** agregar a `bitacoras_apis` una columna de tipo de operación. Cambiaría el esquema de otra tabla compartida.
- **Sí:** dependencia nueva `get_current_active_user_visualizar` que envuelve a `get_current_active_user`. Cada endpoint solo cambia su `Depends` y el límite se valida antes del permiso y de consultar el registro.
- **No:** validar dentro de cada endpoint. Duplicaría código en 4 routers.
- **Sí:** 429 con `detail = "Ha excedido su límite de visualizaciones por hora"`, distinto al de la cuota diaria, para que el cliente sepa cuál límite alcanzó.
- **Sí:** encabezado `Retry-After` en segundos, calculado con la visualización más vieja de la ventana. Le dice al cliente cuándo reintentar.
- **No:** encabezados `X-RateLimit-*`. Quedan fuera, igual que en SPEC 03.
- **Sí:** las visualizaciones siguen contando para la cuota diaria. Son dos límites independientes.
- **No:** tests automatizados. Igual que SPEC 01 a 07, la verificación es manual.

---

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Desplegar antes de aplicar el SQL: `usuarios.api_key_visualizaciones_por_hora` no existe y todas las peticiones fallan. | Aplicar el SQL en producción antes del despliegue. |
| `creado` es `TIMESTAMP` sin zona y se compara con `now()` (`TIMESTAMPTZ`). | PostgreSQL convierte `creado` con la zona de la sesión, la misma con la que `server_default=now()` lo escribió (ver SPEC 03). Verificar con el criterio de "hace 61 minutos". |
| Dos peticiones simultáneas pueden pasar el límite por una o dos visualizaciones. | Se acepta; es un límite de uso razonable, igual que la cuota diaria. |
| Si falla la escritura de la bitácora, esa visualización no cuenta. | Se acepta; la falla queda en el log (SPEC 03). |
| La consulta extra con `LIKE` sobre `api_ruta` añade latencia a cada visualización. | El índice `(usuario_id, creado)` reduce las filas a las de la última hora del usuario; el filtro por segmento se aplica sobre pocas filas. |
| Si un router cambia su prefijo o se agrega otra tabla con `visualizar`, no contaría. Si `root_path` cambia, sigue contando gracias a `contains`. | `VISUALIZAR_RUTAS_PREFIJOS` es la única lista; se actualiza junto con la dependencia en la spec que agregue el endpoint. |

---

## Lo que **no** está en esta spec

- Tests automatizados en `tests/`.
- Límite por hora para endpoints que no son de visualización de PDF, ni para oficios o exhortos.
- Límites separados por tipo de documento.
- Encabezados `X-RateLimit-*` o endpoint de consumo.
- Caché de PDF.
- Cambios a la bitácora, al middleware o a la cuota diaria.

Cada uno de estos, si se hace, va en su propia spec.
