# Consideraciones de mejora - Kitchen Planner API

Este documento resume oportunidades de mejora detectadas tras revisar la base de codigo actual. No propone cambios directos; sirve como guia priorizada para evolucionar seguridad, calidad, operacion y mantenibilidad.

## Contexto tecnico observado

- Framework: FastAPI con Tortoise ORM.
- Base de datos principal: MySQL.
- Base de datos auxiliar para chat/agent: Postgres (LangGraph checkpointer).
- Auth: JWT, OAuth2PasswordBearer.
- Deployment: Docker, AWS Lambda (Mangum).
- Rate limit: SlowAPI.
- Integraciones: Sentry, LangChain/OpenRouter, LangGraph.

## Hallazgos y mejoras recomendadas

### 0) Arquitectura pendiente de definir

- Escalabilidad y despliegue
  - Politica de workers, autoscaling, limites de concurrencia y colas.
  - Estrategia de despliegue blue/green o rolling.
- Separacion de dominios
  - Evaluar si el chat/agent debe ser un servicio separado del core de recetas.
- Arquitectura de eventos/async
  - Definir si se requieren colas para tareas pesadas (chat, sharing masivo, emails).
  - Idempotencia y retries para operaciones criticas.
- Resiliencia
  - Circuit breakers y timeouts end-to-end para dependencias externas (LLM, DB).
- Observabilidad distribuida
  - Trazas con `request_id` correlacionadas entre API, DB y LLM.
- Configuracion multi-entorno
  - Manejo de secrets centralizado y overrides por entorno.
- Migraciones y versionado
  - Estrategia unificada para MySQL + Postgres con versionado y rollback.
- Retencion y privacidad
  - Politicas de retencion de conversaciones y logs.
  - Enmascarado de datos sensibles.
- Caching y invalidacion
  - Definir capas de cache (API, DB, CDN) y reglas de invalidacion.
- Seguridad perimetral
  - API Gateway/WAF, rate limit en edge, restricciones IP si aplica.
- Estrategia de pruebas por capas
  - Contract tests, e2e, performance y chaos testing.
- SLO/SLI
  - Definir objetivos de disponibilidad, latencia y tasa de error.

### 1) Seguridad y autenticacion

- Rotacion y versionado de JWT
  - Considerar incluir un `jti` y manejar revocacion o listas negras si se necesita logout real.
  - Definir caducidad y refresh tokens si se requiere sesiones persistentes.
- Validacion de SECRET_KEY y ALGORITHM
  - Bloquear el arranque si faltan variables criticas como `SECRET_KEY` o `ALGORITHM`.
  - Agregar checks de longitud minima y formato para SECRET_KEY.
- Manejo de errores de autenticacion
  - Respuestas uniformes y sin filtrado de informacion sensible.
  - Evitar diferencias entre "usuario no existe" y "password incorrecta".
- Fortalecer validacion de password
  - La validacion se aplica en el esquema de login/registro; evaluar politicas mas robustas (longitud, historial, bloqueo tras intentos fallidos).
- CSRF y CORS
  - CORS usa una sola variable `FRONTEND_URL`; considerar lista explicita y valores por entorno.
  - Validar que `FRONTEND_URL` no sea None para evitar CORS abierto.

### 2) Manejo de errores y consistencia de respuestas

- Estandarizar respuestas de API
  - Algunas rutas retornan `JSONResponse` directo, otras dicts.
  - Definir un esquema comun de respuestas (`data`, `error`, `meta`).
- Excepciones controladas
  - Evitar `raise e` directo (pierde contexto y no genera respuesta uniforme).
  - Centralizar manejo de errores con middleware o excepciones personalizadas.

### 3) Validacion y esquemas

- Validacion de entrada para IDs
  - Los endpoints de update/delete aceptan `id` sin tipado; preferir `int` con validacion de rango.
- Validacion de fechas
  - En recetas, `schedule_at` y rango de fechas podrian validar coherencia y timezone.
- Esquemas de salida
  - Los modelos de respuesta estan construidos manualmente; considerar Pydantic response models para documentacion y validacion.

### 4) Modelado y base de datos

- Indices y rendimiento
  - Agregar indices para `Recipe.user_id`, `Recipe.schedule_at`, `Recipe.title` si se filtra con frecuencia.
  - En `recipe_user`, ya existe unique index, pero faltan indices para query frecuentes.
- Integridad y consistencia
  - `ingredients` usa JSON con default `[]` en el modelo; verificar compatibilidad con MySQL y migraciones.
  - `RecipeService.scope_filter` retorna `Recipe.all().count()` cuando `filters` es None, pero en ese flujo se espera un query, no un entero.

### 5) Rutas y autorizacion

- Verificacion de ownership
  - `update_recipe` y `delete_recipe` no verifican que la receta pertenezca al usuario autenticado.
  - `shared_recipes` permite compartir recetas sin validar ownership de origen.
- Consistencia en dependencias
  - En `recipe_router` el `Depends(AuthService.get_current_user)` esta duplicado a nivel router y en la firma.
- REST y naming
  - Endpoint `users/me` esta en auth router; puede moverse a user router para consistencia.

### 6) Agent y streaming

- Control de tiempo de espera
  - El timeout se evalua despues de terminar el stream; considerar watchdog durante el stream.
- Estabilidad del stream
  - Manejo de errores genera eventos SSE, pero no hay cierre explicito ni retry.
- Modelo y costos
  - El modelo `openai/gpt-oss-20b` esta hardcodeado; considerar configuracion por entorno.
- Contexto y memoria
  - Validar crecimiento de estado y usar mecanismos de truncado o resumen si hay conversaciones largas.

### 7) Rendimiento y posibles cuellos de botella

- Uvicorn en modo desarrollo
  - `--reload` en `docker-compose.yml` es costoso y usa 1 worker; en carga real puede saturarse.
  - Considerar multi-worker (gunicorn/uvicorn workers) y desactivar reload en prod.
- Conexiones a Postgres para el checkpointer
  - Se mantiene una sola conexion global en `app/db_agent.py`.
  - En concurrencia alta puede bloquear streams; evaluar pool de conexiones.
- Dependencias externas en streaming
  - El stream depende de OpenRouter; latencias externas se traducen en requests largas.
  - Agregar timeouts por chunk y circuit breaker basico.
- Sentry al 100% de trazas
  - `traces_sample_rate=1.0` puede agregar overhead.
  - Reducir sampling en prod y separar errores de performance.
- Consultas sin indices
  - Filtros por `title`, `schedule_at` y `user_id` pueden degradar sin indices.
  - Agregar indices y revisar consultas con EXPLAIN.
- Limite global de rate limit alto
  - `1000/min` no protege de picos; el sistema puede saturarse antes de limitar.
  - Ajustar limites por ruta y por usuario.

### 8) Observabilidad y logging

- Logs estructurados
  - Hay logs en el stream; ampliar a rutas principales con request_id.
- Sentry
  - `send_default_pii=False` esta bien, pero revisar filtrado de datos sensibles en errores.
- Metricas
  - Rate limit tiene configuracion global; agregar metricas de uso por ruta.

### 9) Configuracion y despliegue

- Configuracion centralizada
  - Crear un modulo de settings con Pydantic para validar envs y defaults.
- Docker
  - `docker-compose.yml` incluye `extra_hosts` y DNS especifico; revisar necesidad en prod.
- Lambda
  - Documentar limites de timeout y cold starts para stream y chat.

### 10) Calidad y tests

- Tests
  - No se observan tests; agregar unitarios y de integracion para auth, recetas y sharing.
- Lint/format
  - `ruff` esta en requirements; definir configuracion y hooks para consistencia.
- Tipado
  - Incrementar anotaciones de tipos, especialmente en routers y servicios.

### 11) Documentacion

### 12) Otras optimizaciones posibles

- Cache de lecturas frecuentes
  - Cachear consultas de recetas por usuario/fecha si el patron es repetitivo.
- Paginacion en listados
  - `filter_recipes` ya acepta `offset/per_page` en servicio pero no en el endpoint.
- Normalizacion de payloads
  - `ingredients` en JSON puede crecer; considerar limites de tamaño y validacion.
- Configuracion de timeouts HTTP
  - Definir timeouts globales y por ruta para requests largas.
- Batch inserts y transacciones
  - `shared_its_recipes` ya usa `bulk_create`; envolver con transaccion si se requiere atomicidad.

## Prompts sugeridos para crear placeholders de tests

### Prompt A: placeholders de tests unitarios (FastAPI + servicios)

```text
Actua como un agente de QA para Python. Crea placeholders de tests unitarios para este proyecto FastAPI.

Alcance:
- Tests unitarios para servicios: `app/services/auth_service.py`, `app/services/jwt_service.py`, `app/services/password.py`, `app/services/recipe_service.py`, `app/services/user_service.py`.
- Tests unitarios para recursos y schemas: `app/resources/recipe_resource.py`, `app/schemas/*`.
- No ejecutes los tests, solo crea los archivos y estructura base.

Requisitos:
- Usa `pytest`.
- Cada archivo debe contener al menos 3 tests placeholder con `pass` o `pytest.skip` y nombres descriptivos.
- Incluye fixtures basicas en `tests/conftest.py` (p. ej. `fake_user`, `fake_recipe`, `recipe_payload`).
- Usa mocks donde corresponda para llamadas a base de datos o dependencias externas.
- Mantener los placeholders minimalistas sin implementar logica real.

Salida esperada:
- Nuevos archivos bajo `tests/unit/` con nombres claros.
- `tests/conftest.py`.
```

### Prompt B: placeholders de tests de integracion con BD (MySQL + Tortoise)

```text
Actua como un agente de QA para Python. Crea placeholders de tests de integracion con base de datos para este proyecto FastAPI con Tortoise ORM.

Alcance:
- Tests de integracion para endpoints de recetas y usuarios.
- Conectar a una base de datos de testing (usa variables de entorno o un `DATABASE_URL` temporal).
- Incluye setup y teardown para inicializar Tortoise y limpiar tablas.

Requisitos:
- Usa `pytest` y `pytest-asyncio`.
- Crea archivos bajo `tests/integration/`.
- Cada archivo debe contener al menos 2 tests placeholder con `pass` o `pytest.skip`.
- No ejecuta migraciones reales; define claramente el TODO para integrarlas.
- Evita datos reales; usa datos de ejemplo.

Salida esperada:
- `tests/integration/test_recipes_db.py`.
- `tests/integration/test_users_db.py`.
- fixtures de BD en `tests/conftest.py` o `tests/integration/conftest.py`.
```

### Prompt C: placeholders de tests para agente LangChain/LangGraph

```text
Actua como un agente de QA para Python. Crea placeholders de tests para la capa de agente basada en LangChain/LangGraph en este proyecto.

Alcance:
- Tests para `app/services/agent/chat_stream_service.py`, `app/services/agent/producer.py`, `app/services/agent/event_formatter.py`.
- Tests para el nodo `app/services/agent/nodes/chef/node.py` y herramientas `tools.py`.

Requisitos:
- Usa `pytest` y `pytest-asyncio`.
- Ubica los archivos en `tests/agent/`.
- Cada archivo debe contener al menos 2 tests placeholder con `pass` o `pytest.skip`.
- Mockea dependencias externas: OpenRouter, LangGraph checkpointer, ToolRuntime.
- Aclara TODOs para simulacion de streaming y timeouts.

Salida esperada:
- `tests/agent/test_chat_stream_service.py`.
- `tests/agent/test_producer.py`.
- `tests/agent/test_event_formatter.py`.
- `tests/agent/test_node.py`.
- `tests/agent/test_tools.py`.
```

### Prompt D: mejoras de buenas practicas + tests unitarios asociados

```text
Actua como un agente de mejora de codigo para Python/FastAPI. Aplica mejores practicas al codebase y crea los tests unitarios correspondientes.

Objetivo:
- Refactorizar para claridad, consistencia y seguridad.
- Agregar tests unitarios que validen las mejoras.

Alcance sugerido:
- Manejo de errores uniforme en routers (responses consistentes).
- Validacion estricta de inputs (tipos y rangos).
- Evitar duplicidad de dependencias (auth).
- Extraer configuraciones a settings tipados.
- Asegurar ownership en operaciones de receta.

Requisitos:
- Cambios pequenos y acotados por PR.
- Por cada mejora, crear al menos 1 test unitario.
- Si una mejora afecta un endpoint, agregar un test de ruta basico.
- No ejecutar tests, solo crear placeholders funcionales.

Salida esperada:
- Cambios de codigo documentados.
- Tests en `tests/unit/` o `tests/integration/` segun corresponda.
```

### Prompt E: mejoras de performance + tests de regresion

```text
Actua como un agente de performance para Python/FastAPI. Identifica hotspots y aplica mejoras de performance con tests de regresion.

Alcance sugerido:
- Indices de base de datos y consultas mas eficientes.
- Ajustes en streaming para timeouts y cancelacion.
- Optimizacion de serializacion de respuestas.

Requisitos:
- Cambios incrementales y faciles de revertir.
- Por cada mejora, agregar un test de regresion (puede ser placeholder con TODO claro).
- Documentar el before/after esperado en comentarios de test.

Salida esperada:
- Ajustes de codigo y/o migraciones.
- Tests en `tests/perf/` o `tests/integration/`.
```

### Prompt F: mejoras de seguridad + tests de hardening

```text
Actua como un agente de seguridad para Python/FastAPI. Aplica hardening y agrega tests asociados.

Alcance sugerido:
- Validacion de JWT y manejo de errores uniformes.
- Rate limits por ruta/usuario.
- CORS estricto por entorno.
- Bloqueo de arranque si faltan secrets criticos.

Requisitos:
- Cada hardening debe tener al menos 1 test unitario.
- Si aplica, agregar test de integracion para auth/seguridad.
- No ejecutar tests.

Salida esperada:
- Cambios de codigo y configuracion.
- Tests en `tests/unit/` y/o `tests/integration/`.
```

- README
  - Falta documentar variables de entorno completas, endpoints y ejemplos.
- OpenAPI
  - Agregar tags, descriptions y response models para mejorar la documentacion automatica.

## Priorizacion sugerida

1. Seguridad y autorizacion: ownership de recetas y validacion de secrets.
2. Consistencia de respuestas y errores.
3. Validaciones de entrada y modelos de salida.
4. Observabilidad y logs basicos.
5. Tests minimos y lint.
6. Mejoras en performance e indices.
7. Ajustes en agente y streaming.
8. Ajustes de despliegue (workers, reload, timeouts).

## Notas

- El proyecto mezcla MySQL (core) y Postgres (agent). Documentar claramente este requisito y su razon.
- Revisar que los cambios propuestos se alineen con el alcance de producto.
