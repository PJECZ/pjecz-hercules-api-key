# SPEC 07 — Filtro por órgano jurisdiccional en autoridades

> **Estado:** Aprobado
> **Depende de:** SPEC 01
> **Fecha:** 2026-10-23
> **Objetivo:** Agregar al endpoint `GET /autoridades` el parámetro opcional `organo_jurisdiccional`, normalizado con `safe_string` y validado contra `Autoridad.ORGANOS_JURISDICCIONALES`.

---

## Alcance

**Dentro:**

- Agregar el parámetro `Query` opcional `organo_jurisdiccional` a `autoridades_paginado` en `routers/autoridades.py`.
- Normalizar el valor con `safe_string` (de `core/validation.py`).
- Si el valor normalizado no es una clave de `Autoridad.ORGANOS_JURISDICCIONALES`, responder HTTP 422 con `detail = "El órgano jurisdiccional no es válido"`.
- Si es válido, filtrar por igualdad `Autoridad.organo_jurisdiccional == organo_jurisdiccional`.

**Fuera de alcance (para specs futuras):**

- Modificar `tests/`. La verificación es manual desde `/docs` o con `curl`.
- Agregar el filtro (p. ej. `autoridad_organo_jurisdiccional`) en otros routers que hacen `JOIN` con `Autoridad` (edictos, sentencias, listas de acuerdos, etc.).
- Cambiar el modelo `Autoridad`, el diccionario `ORGANOS_JURISDICCIONALES` o el esquema `AutoridadOut`.
- Cambiar los filtros existentes de `GET /autoridades`, su orden o el filtro `estatus == "A"`.

---

## Modelo de datos

Esta funcionalidad no introduce tablas ni esquemas nuevos. Usa la columna existente `Autoridad.organo_jurisdiccional` (`Enum` no nativo, indexada) y las claves de `Autoridad.ORGANOS_JURISDICCIONALES`:

| Valor válido |
| --- |
| `NO DEFINIDO` |
| `JUZGADO DE PRIMERA INSTANCIA` |
| `JUZGADO DE PRIMERA INSTANCIA ORAL` |
| `PLENO O SALA DEL TSJ` |
| `TRIBUNAL DISTRITAL` |
| `TRIBUNAL DE CONCILIACION Y ARBITRAJE` |

### Forma del filtro

Sigue el mismo patrón que `estado` en `soportes_tickets` y `ubicacion` en `arc_documentos`:

```python
organo_jurisdiccional: Annotated[str | None, Query()] = None,
...
if organo_jurisdiccional and (organo_jurisdiccional := safe_string(organo_jurisdiccional)):
    if organo_jurisdiccional not in Autoridad.ORGANOS_JURISDICCIONALES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="El órgano jurisdiccional no es válido")
    stmt = stmt.where(Autoridad.organo_jurisdiccional == organo_jurisdiccional)
```

### Respuestas HTTP

| Caso | Código | Cuerpo |
| --- | --- | --- |
| Sin `organo_jurisdiccional` o con solo espacios | 200 | Igual que antes de esta spec |
| Valor válido (en cualquier combinación de mayúsculas/minúsculas y acentos) | 200 | Solo autoridades con ese órgano jurisdiccional |
| Valor que no está en `ORGANOS_JURISDICCIONALES` | 422 | `{"detail": "El órgano jurisdiccional no es válido"}` |

---

## Plan de implementación

1. En `routers/autoridades.py`, agregar el parámetro `organo_jurisdiccional` después de `es_extinto` y su filtro después del de `es_extinto`, con la forma descrita arriba. Prueba manual: `GET /autoridades?organo_jurisdiccional=tribunal distrital` regresa solo autoridades con `organo_jurisdiccional == "TRIBUNAL DISTRITAL"`; `GET /autoridades?organo_jurisdiccional=XYZ` responde 422.

---

## Criterios de aceptación

- [ ] `GET /autoridades` muestra en `/docs` el parámetro opcional `organo_jurisdiccional`.
- [ ] `GET /autoridades` sin parámetros responde lo mismo que antes de esta spec (mismo `total` y orden).
- [ ] `GET /autoridades?organo_jurisdiccional=JUZGADO%20DE%20PRIMERA%20INSTANCIA` solo regresa registros con `organo_jurisdiccional == "JUZGADO DE PRIMERA INSTANCIA"` (no incluye `JUZGADO DE PRIMERA INSTANCIA ORAL`).
- [ ] `GET /autoridades?organo_jurisdiccional=tribunal%20de%20conciliación%20y%20arbitraje` regresa los mismos resultados que con `TRIBUNAL DE CONCILIACION Y ARBITRAJE`.
- [ ] `GET /autoridades?organo_jurisdiccional=XYZ` responde 422 con `detail = "El órgano jurisdiccional no es válido"`.
- [ ] `GET /autoridades?organo_jurisdiccional=%20%20%20` responde igual que `GET /autoridades` (el filtro vacío se ignora).
- [ ] `GET /autoridades?organo_jurisdiccional=TRIBUNAL%20DISTRITAL&distrito_clave=<clave>` combina ambos filtros.
- [ ] Solo cambió `routers/autoridades.py` (`git diff --stat` lo confirma).

---

## Decisiones

- **Sí:** el parámetro se llama `organo_jurisdiccional`, igual que el campo de `AutoridadOut` (convención de SPEC 01).
- **Sí:** normalizar con `safe_string` y comparar por igualdad contra las claves de `ORGANOS_JURISDICCIONALES`. Es el mismo patrón de `estado` y `ubicacion`.
- **No:** búsqueda por fragmento (`ILIKE`). `JUZGADO DE PRIMERA INSTANCIA` coincidiría también con `JUZGADO DE PRIMERA INSTANCIA ORAL`.
- **Sí:** 422 con `detail = "El órgano jurisdiccional no es válido"`, mismo estilo que los demás routers.
- **No:** incluir la lista de valores válidos en el mensaje del 422. Sería distinto a los demás routers.
- **Sí:** `NO DEFINIDO` es un valor válido para filtrar, porque está en el diccionario del modelo.
- **No:** extender el filtro a otros routers con `JOIN` a `Autoridad`. Queda para otra spec.
- **No:** tests automatizados. Igual que SPEC 01 a 06, la verificación es manual.

---

## Lo que **no** está en esta spec

- Tests automatizados en `tests/`.
- Cambios a modelos o esquemas.
- Filtro por órgano jurisdiccional en otros routers.

Cada uno de estos, si se hace, va en su propia spec.
