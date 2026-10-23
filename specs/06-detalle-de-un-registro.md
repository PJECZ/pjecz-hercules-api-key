# SPEC 06 — Detalle de un registro en edictos, glosas, listas de acuerdos y sentencias

> **Estado:** Aprobado
> **Depende de:** —
> **Fecha:** 2026-10-22
> **Objetivo:** Agregar a los routers de edictos, glosas, listas de acuerdos y sentencias el endpoint `GET /<tabla>/{id}` que entrega un solo registro activo con su esquema `One*Out`.

---

## Por qué existe esta spec

Hoy estos cuatro módulos solo tienen el listado paginado (`GET /<tabla>`) y la visualización del PDF (`GET /<tabla>/visualizar/{id}`). Un cliente que ya conoce el `id` de un registro tiene que buscarlo en el listado. Los esquemas `OneEdictoOut`, `OneGlosaOut`, `OneListaDeAcuerdoOut` y `OneSentenciaOut` ya existen en `schemas/` pero ningún endpoint los usa.

---

## Alcance

**Dentro:**

- Agregar `GET /edictos/{id}` en `routers/edictos.py` con la función `edictos_detalle`.
- Agregar `GET /glosas/{id}` en `routers/glosas.py` con la función `glosas_detalle`.
- Agregar `GET /listas_de_acuerdos/{id}` en `routers/listas_de_acuerdos.py` con la función `listas_de_acuerdos_detalle`.
- Agregar `GET /sentencias/{id}` en `routers/sentencias.py` con la función `sentencias_detalle`.
- Cada endpoint exige el mismo permiso `>= Permiso.VER` que el listado de su módulo.
- Cada endpoint responde con el esquema `One*Out` existente, con `success=True`, `message="Success"` y el registro en `data`.
- Importar en cada router el esquema `One*Out` correspondiente.

**Fuera de alcance (para specs futuras):**

- Modificar `tests/`. La verificación es manual desde `/docs` o con `curl`.
- Cambiar los esquemas `*Out` o `One*Out` en `schemas/`.
- Endpoints de detalle en otros módulos (oficios, exhortos, autoridades, etc.).
- Cambiar los endpoints existentes `GET /<tabla>` y `GET /<tabla>/visualizar/{id}`.
- Responder `200` con `success=False` cuando el registro no existe.

---

## Modelo de datos

No hay tablas ni esquemas nuevos. Se usan los esquemas que ya existen:

| Router | Modelo | Esquema de respuesta | Permiso |
| --- | --- | --- | --- |
| `routers/edictos.py` | `Edicto` | `OneEdictoOut` | `EDICTOS` |
| `routers/glosas.py` | `Glosa` | `OneGlosaOut` | `GLOSAS` |
| `routers/listas_de_acuerdos.py` | `ListaDeAcuerdo` | `OneListaDeAcuerdoOut` | `LISTAS DE ACUERDOS` |
| `routers/sentencias.py` | `Sentencia` | `OneSentenciaOut` | `SENTENCIAS` |

### Forma de cada endpoint

Ejemplo para edictos; los otros tres son iguales cambiando modelo, esquema y permiso:

```python
@edictos.get("/{id}", response_model=OneEdictoOut)
def edictos_detalle(
    current_user: Annotated[UsuarioInDB, Depends(get_current_active_user)],
    session: Annotated[Session, Depends(get_session)],
    id: int,
):
    """Detalle de un Edicto"""
    if current_user.permissions.get("EDICTOS", 0) < Permiso.VER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    edicto = session.get(Edicto, id)
    if edicto is None or edicto.estatus != "A":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return OneEdictoOut(success=True, message="Success", data=EdictoOut.model_validate(edicto))
```

### Respuestas HTTP

| Caso | Código | Cuerpo |
| --- | --- | --- |
| Sin permiso del módulo `>= VER` | 403 | `{"detail": "Forbidden"}` |
| `id` no es entero | 422 | Validación de FastAPI |
| `id` no existe | 404 | `{"detail": "Not found"}` |
| Registro con `estatus = 'B'` | 404 | `{"detail": "Not found"}` |
| Registro activo | 200 | `{"success": true, "message": "Success", "data": {...}}` |

---

## Plan de implementación

Cada paso deja la API funcionando y se puede hacer commit de él por separado.

1. Agregar `edictos_detalle` (`GET /edictos/{id}`) en `routers/edictos.py`. Prueba manual: `GET /edictos/{id}` de un edicto activo responde 200 con el edicto en `data`; un `id` inexistente responde 404.
2. Agregar `glosas_detalle` (`GET /glosas/{id}`) en `routers/glosas.py`. Prueba manual igual a la del paso 1.
3. Agregar `listas_de_acuerdos_detalle` (`GET /listas_de_acuerdos/{id}`) en `routers/listas_de_acuerdos.py`. Prueba manual igual a la del paso 1.
4. Agregar `sentencias_detalle` (`GET /sentencias/{id}`) en `routers/sentencias.py`. Prueba manual igual a la del paso 1.

---

## Criterios de aceptación

- [ ] Los cuatro endpoints aparecen en `/docs` como `GET /edictos/{id}`, `GET /glosas/{id}`, `GET /listas_de_acuerdos/{id}` y `GET /sentencias/{id}`.
- [ ] Con un `id` de un registro activo, cada endpoint responde 200 con `success = true`, `message = "Success"` y `data` con los mismos campos que ese registro tiene en el listado `GET /<tabla>`.
- [ ] Con un `id` que no existe, cada endpoint responde 404 con `detail = "Not found"`.
- [ ] Con un `id` de un registro con `estatus = 'B'`, cada endpoint responde 404 con `detail = "Not found"`.
- [ ] Con `id = abc`, cada endpoint responde 422.
- [ ] Un usuario sin el permiso del módulo recibe 403 con `detail = "Forbidden"` en el endpoint de ese módulo.
- [ ] `GET /<tabla>` y `GET /<tabla>/visualizar/{id}` responden igual que antes de esta spec en los cuatro módulos.
- [ ] Solo cambiaron `routers/edictos.py`, `routers/glosas.py`, `routers/listas_de_acuerdos.py` y `routers/sentencias.py` (`git diff --stat` lo confirma).

---

## Decisiones

- **Sí:** ruta `/{id}` con `id: int`, igual al parámetro de `/visualizar/{id}`. No choca con `/visualizar/{id}` porque tiene otra profundidad.
- **Sí:** 404 con `HTTPException(detail="Not found")` cuando no existe. Es lo que ya hace `/visualizar/{id}` y el cliente distingue el caso por código HTTP.
- **No:** responder 200 con `success=False` y `data=None`. Oculta el error en el código HTTP y sería distinto a `/visualizar/{id}`.
- **Sí:** un registro con `estatus = 'B'` se trata como inexistente. Los listados solo muestran `estatus = 'A'` y `/visualizar/{id}` ya lo hace así.
- **Sí:** `message = "Success"`, igual que el sobre de `CustomPage` en los listados.
- **Sí:** funciones `<tabla>_detalle`, siguiendo el patrón `<tabla>_paginado` / `<tabla>_visualizar`.
- **Sí:** mismo permiso que el listado de cada módulo (`>= Permiso.VER`).
- **Sí:** usar los esquemas `One*Out` existentes sin cambios.
- **No:** tests automatizados. Igual que SPEC 01 a 05, la verificación es manual.

---

## Lo que **no** está en esta spec

- Tests automatizados en `tests/`.
- Cambios a los esquemas en `schemas/`.
- Endpoints de detalle en otros módulos.
- Cambios a los listados o a `/visualizar/{id}`.

Cada uno de estos, si se hace, va en su propia spec.
