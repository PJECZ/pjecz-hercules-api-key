# SPEC 05 — Oficios de Mi Autoridad, Mi Bandeja de Entrada y Mis Oficios

> **Estado:** Implementado
> **Depende de:** SPEC 01
> **Fecha:** 2026-10-22
> **Objetivo:** Agregar a `routers/ofi_documentos.py` tres endpoints paginados que entregan los oficios de la autoridad del usuario actual, los oficios donde es destinatario y los oficios que él creó.

---

## Por qué existe esta spec

`GET /ofi_documentos` entrega todos los oficios activos y obliga al cliente a filtrar por su cuenta. `pjecz-hercules-flask` ya tiene las vistas "Mi Autoridad", "Mi Bandeja de Entrada" y "Mis Oficios". Esta spec lleva esas tres consultas a la API, filtradas por el usuario dueño de la api_key.

`OfiDocumento` no tiene `autoridad_id`. La autoridad de un oficio es la del usuario que lo creó: `OfiDocumento.usuario_id → Usuario.autoridad_id`.

---

## Alcance

**Dentro:**

- Agregar `autoridad_id: int` a `UsuarioInDB` en `schemas/usuarios.py` y llenarlo en `get_user` de `core/authentication.py` con `usuario.autoridad_id`.
- Agregar a `routers/ofi_documentos.py` los endpoints `GET /ofi_documentos/mi_autoridad`, `GET /ofi_documentos/mi_bandeja_de_entrada` y `GET /ofi_documentos/mis_oficios`.
- Los tres responden `CustomPage[OfiDocumentoOut]`, exigen `OFI DOCUMENTOS >= Permiso.VER` y ordenan por `OfiDocumento.creado.desc()`.
- Filtros opcionales por endpoint según la tabla de la sección Modelo de datos.

**Fuera de alcance (para specs futuras):**

- Modificar `tests/`. La verificación es manual desde `/docs` o con `curl`.
- Cambiar el endpoint existente `GET /ofi_documentos` o sus filtros.
- Cambiar `OfiDocumentoOut` (por ejemplo, agregar `fue_leido` o `con_copia` del destinatario).
- Marcar oficios como leídos.
- Filtros por `esta_archivado`, `esta_cancelado` o `vencimiento_fecha`.
- Endpoints de detalle (`GET /ofi_documentos/{id}`).
- Filtrar por roles `OFICIOS FIRMANTE` / `OFICIOS ESCRITOR` como hace el Flask.

---

## Modelo de datos

No hay tablas ni esquemas de respuesta nuevos. El único cambio de datos es un campo en `UsuarioInDB`:

```python
class UsuarioInDB(UsuarioOut):
    ...
    autoridad_id: int  # nuevo, de usuario.autoridad_id
```

### Endpoints

| Ruta | Joins | Filtros fijos |
| --- | --- | --- |
| `GET /ofi_documentos/mi_autoridad` | `OfiDocumento.usuario` → `Usuario.autoridad` | `OfiDocumento.estatus == "A"`, `Usuario.autoridad_id == current_user.autoridad_id` |
| `GET /ofi_documentos/mi_bandeja_de_entrada` | `OfiDocumento.usuario` → `Usuario.autoridad`, `OfiDocumento.ofi_documentos_destinatarios` | `OfiDocumento.estatus == "A"`, `OfiDocumentoDestinatario.usuario_id == current_user.id`, `OfiDocumentoDestinatario.estatus == "A"` |
| `GET /ofi_documentos/mis_oficios` | — | `OfiDocumento.estatus == "A"`, `OfiDocumento.usuario_id == current_user.id` |

Los joins de "Mi Autoridad" y "Mi Bandeja de Entrada" se hacen siempre, no solo cuando viene un filtro.

### Filtros opcionales

| Parámetro | Tipo | Comparación | mi_autoridad | mi_bandeja_de_entrada | mis_oficios |
| --- | --- | --- | --- | --- | --- |
| `anio` | `int`, `Query(ge=1900, le=2100)` | `OfiDocumento.folio_anio == anio` | Sí | Sí | Sí |
| `autoridad_clave` | `str` | `Autoridad.clave ILIKE '%fragmento%'` tras `safe_clave` | No | Sí | No |
| `creado` | `date` | `func.date(OfiDocumento.creado) == creado` | Sí | Sí | Sí |
| `creado_desde` | `date` | `func.date(OfiDocumento.creado) >= creado_desde` | Sí | Sí | Sí |
| `creado_hasta` | `date` | `func.date(OfiDocumento.creado) <= creado_hasta` | Sí | Sí | Sí |
| `descripcion` | `str` | `OfiDocumento.descripcion ILIKE '%fragmento%'` tras `safe_string` | Sí | Sí | Sí |
| `estado` | `str` | `OfiDocumento.estado == estado` tras `safe_string`; 422 `"El estado no es válido"` si no está en `OfiDocumento.ESTADOS` | Sí | Sí | Sí |
| `folio` | `str` | `OfiDocumento.folio ILIKE '%fragmento%'` tras `safe_string` | Sí | Sí | Sí |
| `numero` | `int`, `Query(ge=1)` | `OfiDocumento.folio_num == numero` | Sí | Sí | Sí |
| `usuario_email` | `str` | `Usuario.email == usuario_email` tras `safe_email` | Sí | Sí | No |

Reglas:

- Se reutilizan `safe_clave`, `safe_email`, `safe_string` y `validate_fechas` de `core/validation.py` (SPEC 01).
- `validate_fechas(creado, creado_desde, creado_hasta)` responde 422 si se combina `creado` con el rango o si `creado_desde > creado_hasta`.
- Si un texto queda vacío tras normalizar, el filtro se ignora.
- `estado` se valida igual que en `routers/soportes_tickets.py`.

### Respuestas HTTP

| Caso | Código |
| --- | --- |
| Sin permiso `OFI DOCUMENTOS >= VER` | 403 `Forbidden` |
| Parámetro inválido (`estado`, `autoridad_clave`, `usuario_email`, fechas, `anio`, `numero`) | 422 |
| Éxito, con o sin resultados | 200 |

---

## Plan de implementación

Cada paso deja la API funcionando y se puede hacer commit de él por separado.

1. Agregar `autoridad_id: int` a `UsuarioInDB` en `schemas/usuarios.py` y `autoridad_id=usuario.autoridad_id` en `get_user` de `core/authentication.py`. Prueba manual: `GET /ofi_documentos` sigue respondiendo 200.
2. Agregar `GET /ofi_documentos/mis_oficios` con sus filtros. Prueba manual: `GET /ofi_documentos/mis_oficios` solo regresa oficios con `usuario_email` igual al del usuario de la api_key.
3. Agregar `GET /ofi_documentos/mi_autoridad` con sus filtros. Prueba manual: todos los resultados tienen `usuario_autoridad_clave` igual a la del usuario de la api_key.
4. Agregar `GET /ofi_documentos/mi_bandeja_de_entrada` con sus filtros e importar `OfiDocumentoDestinatario`. Prueba manual: cada oficio regresado tiene al usuario de la api_key como destinatario activo en `ofi_documentos_destinatarios`.

---

## Criterios de aceptación

- [x] `UsuarioInDB` tiene `autoridad_id` y `get_user` lo llena con `usuario.autoridad_id`.
- [x] Los tres endpoints aparecen en `/docs` bajo `/ofi_documentos/mi_autoridad`, `/ofi_documentos/mi_bandeja_de_entrada` y `/ofi_documentos/mis_oficios`.
- [x] Un usuario sin permiso `OFI DOCUMENTOS` recibe 403 en los tres.
- [x] `GET /ofi_documentos/mis_oficios` solo regresa oficios con `estatus = 'A'` y `usuario_id` igual al del usuario de la api_key.
- [x] `GET /ofi_documentos/mi_autoridad` solo regresa oficios con `estatus = 'A'` cuyo usuario creador tiene el mismo `autoridad_id` que el usuario de la api_key.
- [x] `GET /ofi_documentos/mi_bandeja_de_entrada` solo regresa oficios con `estatus = 'A'` que tienen un destinatario con `usuario_id` del usuario de la api_key y `estatus = 'A'`.
- [x] Un oficio donde el destinatario del usuario tiene `estatus = 'B'` no aparece en `mi_bandeja_de_entrada`.
- [x] Los resultados de los tres endpoints vienen ordenados por `creado` descendente.
- [x] `?anio=2026&numero=5` regresa solo oficios con `folio_anio = 2026` y `folio_num = 5`.
- [x] `?folio=2026` regresa oficios cuyo `folio` contiene `2026`.
- [x] `?estado=firmado` regresa solo oficios con `estado = 'FIRMADO'`.
- [x] `?estado=PENDIENTE` responde 422 con `detail = 'El estado no es válido'`.
- [x] `?creado=2026-10-01` regresa solo oficios creados ese día.
- [x] `?creado_desde=2026-10-01&creado_hasta=2026-10-15` regresa oficios creados en ese rango, ambos días incluidos.
- [x] `?creado=2026-10-01&creado_desde=2026-09-01` responde 422.
- [x] `?creado_desde=2026-10-15&creado_hasta=2026-10-01` responde 422.
- [x] `?descripcion=informe` regresa oficios cuya descripción contiene `INFORME`.
- [x] `?usuario_email=correo@pjecz.gob.mx` funciona en `mi_autoridad` y `mi_bandeja_de_entrada`, y `?usuario_email=no-es-correo` responde 422.
- [x] `?autoridad_clave=...` filtra por la clave de la autoridad del creador en `mi_bandeja_de_entrada`.
- [x] `GET /ofi_documentos` responde igual que antes de esta spec.
- [x] Solo cambiaron `routers/ofi_documentos.py`, `schemas/usuarios.py` y `core/authentication.py` (`git diff --stat` lo confirma).

---

## Decisiones

- **Sí:** la autoridad de un oficio es la de su usuario creador (`Usuario.autoridad_id`). `OfiDocumento` no tiene `autoridad_id`, y así lo hace el Flask.
- **Sí:** agregar `autoridad_id` a `UsuarioInDB`. Evita una consulta extra por petición; `get_user` ya tiene el objeto `Usuario`.
- **No:** subconsulta en el router para obtener el `autoridad_id` del usuario actual. Necesita un alias de `Usuario` y es más difícil de leer.
- **Sí:** "Mis Oficios" usa `current_user.id`. `UsuarioInDB` no tiene `usuario_id`; su `id` es el del usuario.
- **Sí:** join explícito a `OfiDocumentoDestinatario` en "Mi Bandeja de Entrada", tal como el Flask.
- **No:** `EXISTS` / `.any()` para evitar duplicados. En la práctica no hay destinatarios repetidos por oficio; ver Riesgos.
- **Sí:** `anio` → `folio_anio`, `numero` → `folio_num`, por igualdad. Son las columnas que separan el folio.
- **Sí:** `folio` como fragmento (`ILIKE`). Igual que el Flask (`folio.contains`).
- **Sí:** `creado`, `creado_desde` y `creado_hasta` de tipo `date`, comparados con `func.date(OfiDocumento.creado)`. Reutiliza `validate_fechas` y es lo que un cliente espera al filtrar por día.
- **No:** parámetros `datetime`. Obligan al cliente a mandar horas para filtrar un día.
- **Sí:** exigir `OFI DOCUMENTOS >= VER`. Es el mismo permiso de `GET /ofi_documentos`.
- **No:** filtrar por roles `OFICIOS FIRMANTE` / `OFICIOS ESCRITOR`. La API se basa en permisos por módulo, no en roles.
- **Sí:** `estado` validado contra `OfiDocumento.ESTADOS` con 422, como `soportes_tickets`.
- **No:** tests automatizados. Igual que SPEC 01 a 04, la verificación es manual.

---

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Un usuario con dos destinatarios activos en el mismo oficio lo ve repetido en "Mi Bandeja de Entrada" y el total de la paginación cuenta de más. | Se acepta. Si llega a pasar, una spec futura cambia el join por `EXISTS`. |
| `func.date(OfiDocumento.creado)` impide usar un índice sobre `creado`. | Se acepta; los filtros fijos por usuario o autoridad ya reducen mucho las filas. |
| `creado` se guarda en la zona horaria de la sesión de PostgreSQL (en desarrollo `Etc/UTC`, ver SPEC 03); un oficio creado a las 19:00 de Coahuila puede contar como del día siguiente. | Se acepta en esta spec. Si molesta, una spec futura convierte con `settings.TZ`. |

---

## Lo que **no** está en esta spec

- Tests automatizados en `tests/`.
- Cambios a `GET /ofi_documentos` o a `OfiDocumentoOut`.
- Marcar oficios como leídos.
- Filtros por archivado, cancelado o vencimiento.
- Endpoints de detalle.
- Filtrado por roles de oficios.

Cada uno de estos, si se hace, va en su propia spec.
