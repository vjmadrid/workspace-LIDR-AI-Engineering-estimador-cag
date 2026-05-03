# Instrucciones generales de desarrollo en FastAPI

Estas instrucciones aplican al código dentro de `app/`.

## Diseño de API

- Usa FastAPI siguiendo una separación clara entre routers, schemas, servicios y persistencia.
- Los routers deben ser finos: validan entrada, llaman a servicios y devuelven respuestas.
- La lógica de negocio debe vivir fuera de los endpoints.
- Usa nombres de rutas, tags y modelos consistentes.
- Mantén compatibilidad hacia atrás salvo que la tarea pida explícitamente romperla.
- Mantén prefijos versionados como `/api/v1` cuando el endpoint forme parte de un contrato público.
- Evita que los endpoints conozcan detalles de infraestructura externa.
- Convierte excepciones de dominio a respuestas HTTP en la capa de router o mediante exception handlers.
- No devuelvas estructuras ad hoc si existe o debe existir un modelo de respuesta.

## Estructura recomendada

Cuando encaje con el proyecto, favorece una estructura similar a:

```text
app/
├── main.py
├── routers/
├── schemas/
├── services/
├── repositories/
├── dependencies/
├── core/
└── tests/
```

No reorganices todo el proyecto sin necesidad.

En este repositorio, respeta la separación actual cuando aplique:

- `app/routers`: rutas y adaptación HTTP.
- `app/requests`: modelos de entrada de API.
- `app/response`: modelos de salida de API.
- `app/dtos`: estructuras internas entre servicios.
- `app/services`: casos de uso y coordinación de lógica de negocio.
- `app/core`: utilidades transversales e integración base.

## Pydantic y schemas

- Usa modelos Pydantic para request y response bodies
- Separa modelos de entrada, salida y dominio cuando sea útil
- No expongas directamente modelos internos o de base de datos si contienen campos sensibles
- Define response_model en los endpoints cuando aplique
- Usa validaciones declarativas de Pydantic antes que validaciones manuales dispersas
- Usa `Field` para restricciones, ejemplos y documentación cuando mejore el contrato.
- Centraliza validaciones complejas en modelos o servicios, no repartidas por el router.
- Mantén los modelos sincronizados con `specs/contracts` cuando existan schemas JSON.
- Evita nombres ambiguos como `data` o `payload` en contratos públicos si puede usarse lenguaje de dominio.

## Endpoints

- Usa APIRouter
- Define códigos HTTP explícitos cuando no sean 200
- Usa HTTPException para errores esperados de API
- Devuelve errores consistentes.
- Evita bloquear el event loop con operaciones síncronas pesadas dentro de endpoints async
- Define `summary`, `description` y `operation_id` cuando ayuden a consumidores o documentación OpenAPI.
- Usa códigos HTTP semánticos: 400 para entrada inválida de negocio, 401/403 para acceso, 404 para recursos inexistentes, 409 para conflictos y 500 solo para fallos inesperados.
- No captures excepciones genéricas para devolver siempre 500 si eso oculta errores de validación o dominio.
- Mantén respuestas de error con una forma estable y documentada.
- Evita side effects en endpoints `GET`.
- Para operaciones lentas, proporciona feedback claro, timeouts razonables o diseño asíncrono si aplica.

## Dependencias

- Usa Depends para autenticación, autorización, sesiones de base de datos y configuración por request
- Mantén las dependencias pequeñas y testeables
- No escondas lógica de negocio compleja dentro de dependencias
- Usa dependencias para construir servicios o clientes cuando mejore testabilidad.
- Evita crear clientes externos costosos en cada request si pueden reutilizarse con seguridad.
- Mantén la configuración centralizada; no leas variables de entorno directamente en routers.

## Async

- Usa async def cuando el stack sea realmente asíncrono
- No mezcles clientes síncronos dentro de rutas async sin aislarlos correctamente.
- Si una operación es CPU-bound, no la ejecutes directamente en el event loop
- Si el servicio usa librerías síncronas, considera endpoint síncrono o ejecución en threadpool según el caso.
- No marques todo como `async` por defecto; elige según dependencias reales y coste operativo.
- Define timeouts para llamadas I/O y trata cancelaciones cuando haya tareas largas.

## Seguridad

- Valida autenticación y autorización en endpoints protegidos.
- No devuelvas trazas internas al cliente.
- No registres tokens, cookies, cabeceras sensibles ni datos personales innecesarios.
- Configura CORS de forma restrictiva, no con * salvo en desarrollo controlado.
- Valida tamaño, formato y contenido de entradas grandes.
- No incluyas claves, datos sensibles ni respuestas crudas de servicios externos en errores HTTP.
- Devuelve mensajes de error útiles para el cliente sin filtrar detalles internos.
- Usa configuración por entorno para CORS, credenciales y servicios externos.

## Configuración y ciclo de vida

- Crea la app desde una factory como `create_app()` cuando se necesite configurar routers, middleware o handlers.
- Registra routers de forma explícita y evita imports con side effects.
- Usa lifespan/startup solo para inicialización necesaria y observable.
- Mantén health checks simples y sin dependencias externas innecesarias.
- Centraliza exception handlers si varios routers comparten traducción de errores.

## Testing FastAPI

- Usa TestClient o cliente async según el diseño del proyecto.
- Testea endpoints con casos de éxito, errores de validación, autorización y recursos inexistentes.
- Mockea servicios externos.
- Añade tests de regresión para bugs corregidos.
- Verifica `status_code`, forma del JSON y efectos observables relevantes.
- Añade tests de contrato cuando cambien modelos expuestos.
- Usa dependency overrides o monkeypatching para sustituir servicios.
- Evita tests que dependan de claves API, red o configuración local no documentada.

## OpenAPI

- Mantén summaries, descriptions y tags claros cuando el endpoint sea público.
- Usa ejemplos cuando ayuden a consumidores de la API.
- No expongas endpoints internos accidentalmente.
- Revisa que request/response models aparezcan correctamente en la documentación generada.
- Mantén tags consistentes por dominio funcional, no por detalle técnico.
- No documentes como público lo que sea experimental o interno sin dejarlo claro.

## Validación final

Antes de terminar cambios en FastAPI, intenta ejecutar los tests específicos de API, por ejemplo:

```bash
pytest ./tests
```

Para cambios de contratos o schemas, intenta ejecutar también:

```bash
pytest ./tests/specs
```

Si modificas rutas, revisa manualmente que la app arranca y que OpenAPI no se rompe.
