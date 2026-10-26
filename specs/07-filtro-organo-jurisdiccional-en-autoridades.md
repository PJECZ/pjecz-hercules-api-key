# SPEC 07 — Filtro por órgano jurisdiccional en autoridades

> **Estado:** Implementado
> **Depende de:** SPEC 01
> **Fecha:** 2026-10-23
> **Objetivo:** Agregar al endpoint `GET /autoridades` el parámetro opcional `organo_jurisdiccional`, que acepta uno o más valores separados por comas, cada uno normalizado con `safe_string` y validado contra `Autoridad.ORGANOS_JURISDICCIONALES`.

---

## Alcance

**Dentro:**

- Agregar el parámetro `Query` opcional `organo_jurisdiccional` a `autoridades_paginado` en `routers/autoridades.py`.
- Aceptar uno o más valores separados por comas, por ejemplo `PLENO O SALA DEL TSJ,TRIBUNAL DE CONCILIACION Y ARBITRAJE`.
- Separar por comas **antes** de normalizar, y normalizar cada valor con `safe_string` (de `core/validation.py`).
- Descartar los valores vacíos (p. ej. `A,,B` o `A,`) y los repetidos.
- Si algún valor normalizado no es una clave de `Autoridad.ORGANOS_JURISDICCIONALES`, responder HTTP 422 con `detail = "El órgano jurisdiccional no es válido"`.
- Si todos son válidos, filtrar con `Autoridad.organo_jurisdiccional.in_(...)`, es decir, autoridades de uno **u** otro órgano jurisdiccional.

**Fuera de alcance (para specs futuras):**

- Modificar `tests/`. La verificación es manual desde `/docs` o con `curl`.
- Agregar el filtro (p. ej. `autoridad_organo_jurisdiccional`) en otros routers que hacen `JOIN` con `Autoridad` (edictos, sentencias, listas de acuerdos, etc.).
- Cambiar el modelo `Autoridad`, el diccionario `ORGANOS_JURISDICCIONALES` o el esquema `AutoridadOut`.
- Cambiar los filtros existentes de `GET /autoridades`, su orden o el filtro `estatus == "A"`.
- Aceptar valores múltiples en otros parámetros o routers.

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

Ninguna clave contiene comas, por eso la coma sirve como separador sin ambigüedad.

### Forma del filtro

Parte del patrón de `estado` en `soportes_tickets` y `ubicacion` en `arc_documentos`, extendido a una lista:

```python
organo_jurisdiccional: Annotated[str | None, Query()] = None,
...
if organo_jurisdiccional:
    organos_jurisdiccionales = list(dict.fromkeys(o for o in map(safe_string, organo_jurisdiccional.split(",")) if o))
    if organos_jurisdiccionales:
        if any(o not in Autoridad.ORGANOS_JURISDICCIONALES for o in organos_jurisdiccionales):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="El órgano jurisdiccional no es válido")
        stmt = stmt.where(Autoridad.organo_jurisdiccional.in_(organos_jurisdiccionales))
```

- `split(",")` va antes de `safe_string` para que el límite de 256 caracteres de `safe_string` aplique a cada valor y no a la cadena completa.
- `dict.fromkeys` quita repetidos conservando el orden.
- Con un solo valor, `in_([valor])` equivale a la igualdad del paso 1.

### Respuestas HTTP

| Caso | Código | Cuerpo |
| --- | --- | --- |
| Sin `organo_jurisdiccional`, con solo espacios o solo comas | 200 | Igual que antes de esta spec |
| Un valor válido (en cualquier combinación de mayúsculas/minúsculas y acentos) | 200 | Solo autoridades con ese órgano jurisdiccional |
| Dos o más valores válidos separados por comas | 200 | Autoridades con cualquiera de esos órganos jurisdiccionales |
| Al menos un valor que no está en `ORGANOS_JURISDICCIONALES` | 422 | `{"detail": "El órgano jurisdiccional no es válido"}` |

---

## Plan de implementación

1. ~~En `routers/autoridades.py`, agregar el parámetro `organo_jurisdiccional` después de `es_extinto` y su filtro después del de `es_extinto`, filtrando por igualdad con un solo valor.~~ Hecho en el commit `09d3f85`.
2. En `routers/autoridades.py`, reemplazar el filtro de igualdad por la forma con lista descrita arriba. Prueba manual: `GET /autoridades?organo_jurisdiccional=PLENO O SALA DEL TSJ,TRIBUNAL DE CONCILIACION Y ARBITRAJE` regresa autoridades de ambos órganos y ninguna de otros; `GET /autoridades?organo_jurisdiccional=TRIBUNAL DISTRITAL,XYZ` responde 422.

---

## Criterios de aceptación

- [x] `GET /autoridades` muestra en `/docs` el parámetro opcional `organo_jurisdiccional`.
- [x] `GET /autoridades` sin parámetros responde lo mismo que antes de esta spec (mismo `total` y orden).
- [x] `GET /autoridades?organo_jurisdiccional=JUZGADO%20DE%20PRIMERA%20INSTANCIA` solo regresa registros con `organo_jurisdiccional == "JUZGADO DE PRIMERA INSTANCIA"` (no incluye `JUZGADO DE PRIMERA INSTANCIA ORAL`).
- [x] `GET /autoridades?organo_jurisdiccional=tribunal%20de%20conciliación%20y%20arbitraje` regresa los mismos resultados que con `TRIBUNAL DE CONCILIACION Y ARBITRAJE`.
- [x] `GET /autoridades?organo_jurisdiccional=PLENO%20O%20SALA%20DEL%20TSJ,TRIBUNAL%20DE%20CONCILIACION%20Y%20ARBITRAJE` regresa autoridades de ambos órganos; su `total` es la suma de los `total` de cada valor por separado.
- [x] `GET /autoridades?organo_jurisdiccional=pleno%20o%20sala%20del%20tsj%20,%20%20tribunal%20distrital` (minúsculas y espacios alrededor de la coma) funciona igual que con los valores normalizados.
- [x] `GET /autoridades?organo_jurisdiccional=TRIBUNAL%20DISTRITAL,TRIBUNAL%20DISTRITAL` regresa lo mismo que con un solo `TRIBUNAL DISTRITAL`.
- [x] `GET /autoridades?organo_jurisdiccional=TRIBUNAL%20DISTRITAL,,` regresa lo mismo que con un solo `TRIBUNAL DISTRITAL` (los vacíos se ignoran).
- [x] `GET /autoridades?organo_jurisdiccional=XYZ` responde 422 con `detail = "El órgano jurisdiccional no es válido"`.
- [x] `GET /autoridades?organo_jurisdiccional=TRIBUNAL%20DISTRITAL,XYZ` responde 422 con `detail = "El órgano jurisdiccional no es válido"` (basta un valor inválido).
- [x] `GET /autoridades?organo_jurisdiccional=%20%20%20` y `GET /autoridades?organo_jurisdiccional=,,` responden igual que `GET /autoridades` (el filtro vacío se ignora).
- [x] `GET /autoridades?organo_jurisdiccional=TRIBUNAL%20DISTRITAL&distrito_clave=<clave>` combina ambos filtros.
- [x] Solo cambió `routers/autoridades.py` (`git diff --stat` lo confirma).

---

## Decisiones

- **Sí:** el parámetro se llama `organo_jurisdiccional`, igual que el campo de `AutoridadOut` (convención de SPEC 01). Se mantiene en singular aunque acepte varios valores, para no romper a quien ya lo usa con uno.
- **Sí:** varios valores en un solo parámetro separados por comas (`?organo_jurisdiccional=A,B`). Es más fácil de escribir en `/docs` y en `curl` que repetir el parámetro.
- **No:** repetir el parámetro (`?organo_jurisdiccional=A&organo_jurisdiccional=B`) como `list[str]`. Cambiaría el tipo del parámetro y la forma en que se ve en `/docs`.
- **Sí:** combinar los valores con OR (`IN`). Una autoridad solo tiene un órgano jurisdiccional, así que AND nunca regresaría nada.
- **Sí:** normalizar cada valor con `safe_string` y comparar por igualdad contra las claves de `ORGANOS_JURISDICCIONALES`. Es el mismo patrón de `estado` y `ubicacion`.
- **No:** búsqueda por fragmento (`ILIKE`). `JUZGADO DE PRIMERA INSTANCIA` coincidiría también con `JUZGADO DE PRIMERA INSTANCIA ORAL`.
- **Sí:** 422 si **cualquier** valor es inválido, en lugar de ignorar los inválidos. Ignorarlos ocultaría errores de escritura del cliente.
- **Sí:** 422 con `detail = "El órgano jurisdiccional no es válido"`, mismo estilo que los demás routers.
- **No:** incluir en el mensaje del 422 la lista de valores válidos ni cuál fue el inválido. Sería distinto a los demás routers.
- **Sí:** ignorar valores vacíos y repetidos entre comas, en lugar de responder 422.
- **Sí:** `NO DEFINIDO` es un valor válido para filtrar, porque está en el diccionario del modelo.
- **No:** extender el filtro a otros routers con `JOIN` a `Autoridad`. Queda para otra spec.
- **No:** tests automatizados. Igual que SPEC 01 a 06, la verificación es manual.

---

## Lo que **no** está en esta spec

- Tests automatizados en `tests/`.
- Cambios a modelos o esquemas.
- Filtro por órgano jurisdiccional en otros routers.
- Valores múltiples en otros parámetros.

Cada uno de estos, si se hace, va en su propia spec.
