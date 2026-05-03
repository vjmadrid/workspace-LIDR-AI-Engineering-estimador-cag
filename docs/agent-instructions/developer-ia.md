# Instrucciones para desarrollo de IA y LLMs

Estas instrucciones aplican cuando se modifique código relacionado con prompts, modelos, proveedores de IA, estimaciones generadas por LLMs o procesamiento de entradas que se envían a un modelo.

## Diseño

- Aísla clientes de OpenAI, Anthropic u otros proveedores en servicios o módulos `core`.
- Evita que routers, UI o scripts conozcan detalles de construcción de prompts o proveedores.
- Separa construcción de prompts, llamada al proveedor, parseo de respuesta y transformación a DTOs.
- Mantén prompts, ejemplos y ensamblado de contexto en `app/context` o módulos equivalentes.
- Normaliza respuestas externas a DTOs internos antes de pasarlas al resto de la aplicación.
- No mezcles reglas de negocio con texto de prompt si pueden expresarse como validaciones o servicios testeables.

## Prompts y contexto

- Mantén prompts versionables, legibles y con nombres de dominio claros.
- Evita duplicar instrucciones entre prompts; extrae bloques reutilizables cuando cambien juntos.
- Incluye ejemplos solo cuando mejoren de forma clara la calidad o estabilidad de la salida.
- No añadas datos sensibles reales en ejemplos, fixtures o documentación.
- Documenta brevemente supuestos importantes del prompt cuando no sean evidentes.
- Trata cambios de prompt como cambios de comportamiento: revisa tests, escenarios y contratos afectados.

## Proveedores y configuración

- Configura modelos, endpoints, claves, timeouts y límites mediante configuración centralizada.
- Define timeouts y manejo explícito para rate limits, respuestas vacías, errores de red y formato inesperado.
- No hardcodees nombres de modelos si ya existe una constante o setting adecuado.
- Encapsula diferencias entre proveedores para que el resto del código trabaje con una interfaz estable.
- Valida y normaliza la respuesta del proveedor antes de construir el response model.
- No hagas llamadas reales a proveedores en tests unitarios.

## Seguridad y privacidad

- No registres prompts completos, transcripciones completas, claves, tokens ni respuestas crudas de LLMs.
- Sanitiza o resume entradas de usuario antes de incluirlas en logs, errores o trazas.
- Valida tamaño, formato y contenido de entradas grandes como transcripciones antes de enviarlas al modelo.
- Evita exponer detalles internos del prompt o del proveedor en errores HTTP o UI.
- No incluyas datos personales o confidenciales en fixtures, ejemplos o snapshots.
- Aplica mínimos privilegios a claves y credenciales usadas por proveedores de IA.

## Salidas estructuradas

- Prefiere salidas estructuradas y validadas cuando el resultado deba alimentar lógica de negocio.
- Usa modelos Pydantic, DTOs o schemas para validar campos obligatorios, tipos y rangos.
- Maneja respuestas parciales o inválidas como errores esperados, no como fallos genéricos.
- Mantén los contratos de respuesta sincronizados con `specs/contracts` cuando existan.
- Añade fallback o mensajes claros cuando el proveedor no pueda generar una respuesta útil.

## Coste, tokens y rendimiento

- Calcula o estima tokens y coste en una capa clara cuando sea relevante para el producto.
- Evita enviar contexto innecesario al modelo; conserva solo la información que aporte valor.
- Cachea resultados solo si es correcto para privacidad, frescura y semántica del caso de uso.
- Registra métricas agregadas útiles, como latencia, proveedor, modelo y errores, sin datos sensibles.
- Considera límites de tamaño y truncado explícito para entradas largas.

## Testing y evaluación

- Mockea proveedores de IA en tests unitarios y de API.
- Añade escenarios representativos para casos normales, entradas vacías, respuestas inválidas y errores de proveedor.
- Usa tests de contrato cuando cambie la forma de request o response.
- Mantén fixtures deterministas y libres de secretos.
- Para cambios importantes de prompt, revisa manualmente al menos un caso de éxito y un caso límite.
- Añade tests de regresión cuando se corrijan errores de parseo, coste, tokens o formato de salida.
