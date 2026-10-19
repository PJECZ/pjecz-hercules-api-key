# SPEC 01 — Filtros opcionales en los endpoints paginados

> **Estado:** Aprobado
> **Depende de:** —
> **Fecha:** 2026-10-18
> **Objetivo:** Agregar parámetros de consulta opcionales a los endpoints paginados para filtrar por clave, fragmento de texto, fecha y expediente, validados con funciones de `core/validation.py`.

---

## Alcance

**Dentro:**

- Crear `src/pjecz_hercules_api_key/core/validation.py` con las funciones de validación y normalización.
- Agregar parámetros `Query` opcionales al endpoint `GET ""` de cada router listado en la tabla de filtros.
- Filtros por campos propios de la tabla como texto completo: `expediente`, `email`, `usuario_email`, `curp`.
- Filtros por campos propios de la tabla como texto parcial: `apellido_paterno`, `apellido_materno`, `clave`, `demandado`, `descripcion`, `edificio`, `*_edificio`, `nombre`, `*_nombre`, `nombres`.
- Filtros por campos propios de la tabla como entero: `expediente_anio` / `anio`, `expediente_num` / `expediente_numero`.
- Filtros por campos propios de la tabla como CURP parcial: `funcionario_curp`, `usuario_curp`.
- Filtros por campos propios de la tabla como texto completo que debe ser una opcion predeterminada en el modelo: `estado`
- Filtros por clave de relaciones (`autoridad_clave`, `distrito_clave`, `domicilio_edificio`, `materia_clave`, etc.) mediante `JOIN`.
- Filtros por campos booleanos (`es_*`, `en_*`)
- Filtros por fecha directa: `fecha`, `*_fecha`
- Rango de fechas con `fecha_desde` y `fecha_hasta` en los routers que tienen `fecha`.
- Responder HTTP 422 con `detail` cuando un parámetro no pasa la validación.

**Fuera de alcance (para specs futuras):**

- Modificar `tests/`. La verificación es manual desde `/docs` o con `curl`.
- Modificar modelos, esquemas, `main.py` o cualquier archivo fuera de `routers/` y `core/validation.py`.
- Filtros por `id` o por UUID de relaciones (`ofi_documento_id`, `rol_id`, etc.).
- Filtros por campos `datetime`.
- Filtrar por `municipio_origen_clave` / `municipio_destino_clave` en exhortos (la clave de municipio no es única entre estados).
- Endpoints de detalle (`GET /{id}`); hoy no existen.
- Cambiar el orden de los resultados o el filtro `estatus == "A"` existente.

---

## Modelo de datos

Esta funcionalidad no introduce tablas ni esquemas nuevos. Cada parámetro es el nombre de un campo que ya existe en el esquema `*Out` del router.

### Funciones de `core/validation.py`

| Función | Entrada | Salida | Regla |
| --- | --- | --- | --- |
| `safe_clave(clave, max_len)` | `str` | `str` | `safe_string`, luego debe cumplir `^[A-Z0-9_-]+$`; si no, 422. |
| `safe_curp(texto)` | `str` | `str` | `strip`, luego debe cumplir `^[a-zA-Z]{4}\d{6}[a-zA-Z]{6}[A-Z0-9]{2}$`. |
| `safe_email(texto)` | `str` | `str` | `strip`, luego debe cumplir `^[\w.-]+@[\w.-]+\.\w+$`. |
| `safe_expediente(expediente)` | `str` | `str` | `safe_string`, luego debe cumplir `^\d{1,5}/(19\|20)\d{2}(-[A-Z0-9]+)?$` (ej. `123/2024`, `45/2023-II`); quita ceros a la izquierda del número; si no cumple, 422. |
| `safe_string(texto, max_len)` | `str` | `str` | `strip`, colapsa espacios múltiples en uno, convierte a MAYÚSCULAS, aplica `unidecode` a todo **excepto** `Ñ` y `Ü` (se conservan), recorta a `max_len`. |
| `validate_fechas(fecha, fecha_desde, fecha_hasta)` | `date \| None` ×3 | `None` | 422 si se combina `fecha` con `fecha_desde` o `fecha_hasta`; 422 si `fecha_desde > fecha_hasta`. |

Convenciones:

- Las funciones lanzan `HTTPException(status_code=422, detail="...")` directamente, porque no se puede registrar un manejador de excepciones en `main.py`.
- Si después de normalizar un texto queda vacío, el filtro se ignora (equivale a no enviarlo).
- Los parámetros `int` (`expediente_anio`, `anio`, `expediente_num`, `expediente_numero`) se declaran con `Query(ge=...)`: año `ge=1900, le=2100`, número `ge=1`. FastAPI responde 422 por sí mismo.
- Los parámetros `date` usan el tipo `date` de FastAPI (formato `AAAA-MM-DD`).

### Tipos de comparación

| Parámetro | Comparación |
| --- | --- |
| `apellido_paterno`, `apellido_materno`, `clave`, `demandado`, `descripcion`, `edificio`, `*_edificio`, `nombre`, `*_nombre`, `nombres` | `ILIKE '%fragmento%'` tras `safe_string`. |
| `clave`, `*_clave` | `ILIKE '%fragmento%'` tras `safe_clave`. |
| `curp`, `funcionario_curp`, `usuario_curp` | Igualdad tras `safe_curp`. |
| `email` | Igualdad tras `safe_email`. |
| `fecha` | Igualdad. |
| `estado` | Igualdad tras `safe_string`. |
| `fecha_desde` / `fecha_hasta` | `>=` / `<=`. |
| `expediente` | Igualdad exacta tras `safe_expediente`. |
| `expediente_anio`, `anio`, `expediente_num`, `expediente_numero` | Igualdad. |

### Tabla de filtros por router

`F` = `fecha`, `fecha_desde`, `fecha_hasta`.

| Router | Parámetros | Joins necesarios |
| --- | --- | --- |
| `arc_documentos` | `actor`, `anio`, `autoridad_clave`, `demandado`, `expediente`, `expediente_numero`, `ubicacion` | `Autoridad` |
| `arc_documentos_tipos` | `nombre` | — |
| `arc_juzgados_extintos` | `clave`, `descripcion`, `distrito_clave` | `Distrito` |
| `arc_remesas` | `autoridad_clave` | `Autoridad` |
| `arc_remesas_documentos` | *(sin filtros)* | — |
| `autoridades` | `clave`, `descripcion`, `distrito_clave`, `materia_clave`, `es_jurisdiccional`, `es_notaria`, `es_extinto` | `Distrito`, `Materia` |
| `dgt_depositos` | `clave`, `descripcion` | — |
| `dgt_digitalizaciones` | `autoridad_clave`, `dgt_ruta_clave`, `descripcion`, `expediente`, `expediente_anio`, `expediente_num` | `Autoridad`, `DgtRuta` |
| `dgt_entregas` | `autoridad_clave`, `dgt_ruta_clave`, `descripcion`, `expediente`, `expediente_anio`, `expediente_num` | `Autoridad`, `DgtRuta` |
| `dgt_plataformas` | `descripcion` | — |
| `dgt_plataformas_autoridades` | `autoridad_clave` | `Autoridad` |
| `dgt_plataformas_endpoints` | `descripcion` | — |
| `dgt_rutas` | `clave`, `autoridad_clave` (columna propia), `dgt_tipo_clave` | `DgtTipo` |
| `dgt_tipos` | `clave`, `descripcion` | — |
| `distritos` | `clave`, `nombre`, `es_distrito`, `es_jurisdiccional` | — |
| `domicilios` | `distrito_clave` | `Distrito` |
| `edictos` | `autoridad_clave`, `distrito_clave`, F, `descripcion`, `expediente` | `Autoridad`, `Distrito` |
| `estados` | `clave`, `nombre` | — |
| `exh_areas` | `clave`, `nombre` | — |
| `exh_exhortos` | `autoridad_clave`, `exh_area_clave`, `materia_clave` (columna propia) | `Autoridad`, `ExhArea` |
| `exh_exhortos_archivos` | *(sin filtros)* | — |
| `exh_exhortos_partes` | `nombre`, `apellido_paterno`, `apellido_materno` | — |
| `exh_tipos_diligencias` | `clave`, `descripcion` | — |
| `funcionarios` | `curp`, `nombres`, `apellido_paterno`, `apellido_materno` | — |
| `funcionarios_oficinas` | `oficina_clave`, `funcionario_curp` | `Funcionario`, `Oficina` |
| `glosas` | `autoridad_clave`, `distrito_clave`, F, `descripcion`, `expediente` | `Autoridad`, `Distrito` |
| `listas_de_acuerdos` | `autoridad_clave`, `distrito_clave`, F, `descripcion` | `Autoridad`, `Distrito` |
| `materias` | `clave`, `nombre` | — |
| `materias_tipos_juicios` | `materia_clave`, `descripcion` | `Materia` |
| `modulos` | `nombre` | — |
| `municipios` | `clave`, `nombre`, `estado_clave` | `Estado` |
| `oficinas` | `clave`, `descripcion`, `distrito_clave`, `domicilio_edificio` | `Distrito`, `Domicilio` |
| `ofi_documentos` | `usuario_autoridad_clave`, `usuario_email`, `descripcion` | `Usuario`, `Autoridad` |
| `ofi_documentos_adjuntos` | `descripcion` | — |
| `ofi_documentos_destinatarios` | `usuario_autoridad_clave`, `usuario_email` | `Usuario`, `Autoridad` |
| `permisos` | `modulo_nombre`, `rol_nombre` | `Modulo`, `Rol` |
| `redams` | `autoridad_clave`, `distrito_clave`, F, `nombre`, `expediente` | `Autoridad`, `Distrito` |
| `repsvm_agresores` | `distrito_clave`, `nombre` | `Distrito` |
| `roles` | `nombre` | — |
| `sentencias` | `autoridad_clave`, `distrito_clave`, `materia_clave`, F, `descripcion`, `expediente`, `expediente_anio`, `expediente_num` | `Autoridad`, `Distrito`, `MateriaTipoJuicio`, `Materia` |
| `soportes_categorias` | `nombre` | — |
| `soportes_tickets` | `estado`, `funcionario_curp`, `soporte_categoria_nombre`, `usuario_email` | `Funcionario`, `Soporte Categoria`, `Usuario` |
| `usuarios` | `autoridad_clave`, `distrito_clave`, `curp`, `email`, `oficina_clave`, `nombres`, `apellido_paterno`, `apellido_materno` | `Autoridad`, `Distrito`, `Oficina` |
| `usuarios_roles` | `usuario_email`, `rol_nombre` | `Rol`, `Usuario` |

Reglas de los joins:

- Solo se agrega el `JOIN` cuando el parámetro correspondiente viene en la petición.
- `distrito_clave` en tablas que cuelgan de `Autoridad` se resuelve con `Autoridad → Distrito`; si `autoridad_clave` también viene, se reutiliza el mismo join de `Autoridad`.
- `materia_clave` en `sentencias` se resuelve con `MateriaTipoJuicio → Materia`.

---

## Plan de implementación

Cada paso deja la API funcionando y se puede hacer commit de él por separado.

1. Crear `core/validation.py` con `safe_string`, `safe_clave`, `safe_curp`, `safe_email`, `safe_expediente` y `validate_fechas`. Ningún router lo usa todavía. Prueba manual: importar en `python -c` y comprobar `safe_string("  áé  ñü  x ")` → `"AE ÑÜ X"`.
2. Catálogos con `clave` / `nombre` / `descripcion` sin joins: `arc_documentos_tipos`, `dgt_depositos`, `dgt_plataformas`, `dgt_tipos`, `distritos`, `estados`, `exh_areas`, `exh_tipos_diligencias`, `materias`, `modulos`, `roles`, `soportes_categorias`. Prueba manual: `GET /distritos?clave=...` regresa un solo registro.
3. Catálogos con join simple: `arc_juzgados_extintos`, `autoridades`, `domicilios`, `materias_tipos_juicios`, `municipios`, `oficinas`, `repsvm_agresores`. Prueba manual: `GET /autoridades?distrito_clave=...`.
4. Documentos judiciales sin expediente numérico: `edictos`, `glosas`, `listas_de_acuerdos`, `redams`. Incluye `validate_fechas`. Prueba manual: `GET /edictos?fecha_desde=...&fecha_hasta=...`.
5. `sentencias`, con todos sus filtros (incluye el join a `Materia`).
6. Archivo: `arc_documentos`, `arc_remesas`.
7. DGT: `dgt_digitalizaciones`, `dgt_entregas`, `dgt_plataformas_autoridades`, `dgt_rutas`.
8. Exhortos: `exh_exhortos`, `exh_exhortos_partes`.
9. Usuarios: `usuarios`, `usuarios_roles`.
10. Funcionarios y Soportes: `funcionarios`, `funcionarios_oficinas`, `soportes_tickets`.
11. Oficios: `ofi_documentos`, `ofi_documentos_adjuntos`, `ofi_documentos_destinatarios`.

---

## Criterios de aceptación

- [ ] Existe `src/pjecz_hercules_api_key/core/validation.py` con `safe_string`, `safe_clave`, `safe_expediente` y `validate_fechas`.
- [ ] `safe_string("  José   Peña  Güémez ")` regresa `"JOSE PEÑA GÜEMEZ"`.
- [ ] Solo cambiaron archivos en `routers/` y el nuevo `core/validation.py` (`git diff --stat` lo confirma).
- [ ] Cada router de la tabla expone en `/docs` exactamente los parámetros listados, todos opcionales.
- [ ] Sin parámetros, cada endpoint responde lo mismo que antes de esta spec (mismo `total` y orden).
- [ ] `GET /distritos?clave=<clave existente>` regresa `total == 1`.
- [ ] `GET /edictos?descripcion=<fragmento en minúsculas con acentos>` regresa los mismos resultados que con el fragmento en mayúsculas sin acentos.
- [ ] `GET /edictos?fecha=2025-01-15` solo regresa registros con `fecha == "2025-01-15"`.
- [ ] `GET /edictos?fecha_desde=2025-01-01&fecha_hasta=2025-01-31` solo regresa registros dentro de ese rango.
- [ ] `GET /edictos?fecha=2025-01-15&fecha_desde=2025-01-01` responde 422.
- [ ] `GET /edictos?fecha_desde=2025-02-01&fecha_hasta=2025-01-01` responde 422.
- [ ] `GET /sentencias?expediente=abc` responde 422.
- [ ] `GET /sentencias?expediente=0123/2024` filtra igual que `expediente=123/2024`.
- [ ] `GET /sentencias?expediente_anio=1800` responde 422.
- [ ] `GET /autoridades?clave=A%20B!` responde 422.
- [ ] `GET /sentencias?distrito_clave=<clave>&materia_clave=<clave>` solo regresa sentencias de ese distrito y esa materia.
- [ ] `GET /edictos?descripcion=%20%20%20` responde igual que `GET /edictos` (el filtro vacío se ignora).

---

## Decisiones

- **Sí:** filtros por `*_clave` de relaciones con `JOIN`. Es el filtro más útil para documentos judiciales.
- **No:** solo campos propios de la tabla. Dejaría fuera autoridad y distrito.
- **Sí:** filtro por fragmento de `nombre` además de `descripcion`. Muchos catálogos no tienen `descripcion`.
- **No:** `funcionarios.nombre`. Es `@property`, no columna; no se puede usar en SQL.
- **Sí:** el nombre de cada parámetro coincide con el campo del esquema (`anio` y `expediente_numero` en `arc_documentos`; `expediente_anio` y `expediente_num` en los demás).
- **Sí:** HTTP 422 con `detail` ante parámetros inválidos. Es lo mismo que hace FastAPI con los tipos inválidos.
- **No:** HTTP 400 o ignorar el parámetro inválido. Ignorarlo devolvería resultados engañosos.
- **Sí:** `expediente` con comparación exacta tras validar y normalizar el formato. Es más preciso que buscar por fragmento.
- **No:** `expediente` por fragmento (`ILIKE`).
- **Sí:** normalizar texto con `strip`, espacios colapsados, mayúsculas y `unidecode`, conservando `Ñ` y `Ü`. Así se guardan los datos en Hércules.
- **Sí:** `fecha` es excluyente con `fecha_desde` / `fecha_hasta` (422 si se combinan). `fecha_desde` o `fecha_hasta` solos sí se permiten.
- **Sí:** las funciones de validación lanzan `HTTPException(422)` directamente. No se puede tocar `main.py` para registrar un manejador de `MyNotValidParamError`.
- **Sí:** una sola spec, con pasos agrupados por prefijo. Todos los routers siguen el mismo patrón.
- **No:** tests automatizados en esta spec. El usuario limitó el trabajo a routers y `core/validation.py`.

---

## Riesgos

| Riesgo | Mitigación |
| --- | --- |
| `redams.expediente` es `String(256)` y puede guardar formatos que no cumplen `safe_expediente`. | Los registros con formato libre no se encuentran por `expediente`. Si pasa con frecuencia, una spec futura agrega búsqueda por fragmento solo para `redams`. |
| Algunas claves DGT (`String(64)`) podrían tener caracteres fuera de `[A-Z0-9_-]`. | Antes del paso 7, revisar las claves reales de `dgt_depositos`, `dgt_tipos` y `dgt_rutas`; ampliar el patrón de `safe_clave` si hace falta. |
| `unidecode` convertiría `Ñ`/`Ü` en `N`/`U`. | `safe_string` protege esos caracteres antes de aplicar `unidecode` y los restaura después. |
| Los joins podrían duplicar filas o romper el `count` de la paginación. | Todos los joins son muchos-a-uno (hacia el padre), así que no duplican filas. |
| `ILIKE '%x%'` sobre `soportes_tickets.descripcion` (`Text`) puede ser lento. | Se acepta por ahora; la paginación limita la respuesta. |

---

## Lo que **no** está en esta spec

- Tests automatizados en `tests/`.
- Cambios en modelos, esquemas o `main.py`.
- Filtros por `id`, UUID o campos `datetime`.
- Filtros por clave de municipio en exhortos.
- Endpoints de detalle.

Cada uno de estos, si se hace, va en su propia spec.
