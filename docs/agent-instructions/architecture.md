# Arquitectura

## Objetivo

- Mantén el proyecto fácil de evolucionar: cambios pequeños, capas claras y contratos explícitos.
- Prioriza soluciones simples que encajen con la estructura actual antes que rediseños amplios.
- Cuando una decisión tenga impacto en varias capas, documenta brevemente el motivo en el código, README o specs.

## General

- Separa lógica de negocio, entrada/salida, configuración e infraestructura
- Evita que módulos de dominio dependan directamente de frameworks web o UI
- Prefiere inyección de dependencias simple a singletons globales
- Mantén configuración en variables de entorno o ficheros dedicados, no hardcodeada
- Conserva los límites entre `routers`, `requests`, `response`, `dtos`, `services`, `core`, `context` y `config`
- No muevas módulos de forma masiva si una tarea puede resolverse con cambios localizados
- Evita dependencias circulares; si aparecen, extrae contratos, DTOs o helpers a una capa más estable
- Usa nombres de módulos alineados con el lenguaje del dominio del proyecto

## Capas

- `routers`: adaptadores HTTP; deben orquestar, validar errores esperados y delegar en servicios
- `requests` y `response`: contratos de entrada y salida expuestos por API
- `dtos`: estructuras internas para transportar datos entre servicios o utilidades
- `services`: casos de uso y lógica de negocio; no deben depender de detalles HTTP
- `core`: utilidades transversales, integraciones base y lógica reusable sin conocimiento de endpoints
- `context`: prompts, ejemplos y ensamblado de contexto; mantén aquí el contenido de apoyo a LLMs
- `config`: lectura y validación de configuración; evita leer variables de entorno desde cualquier capa

## Contratos y compatibilidad

- Trata los schemas de `specs/contracts` como contratos públicos cuando existan
- Si cambia un request o response, actualiza modelos, tests y specs en el mismo cambio
- Mantén compatibilidad hacia atrás salvo que la tarea pida romperla explícitamente
- Versiona rutas o contratos cuando el cambio sea incompatible para consumidores existentes
- Añade pruebas de regresión para bugs que afecten respuestas, errores o cálculo de estimaciones

## Configuración

- Centraliza configuración en `app/config.py` o módulos equivalentes
- Valida configuración obligatoria al arrancar o al construir servicios, no en mitad del flujo de negocio
- Usa defaults seguros para desarrollo y tests; no uses defaults silenciosos para secretos productivos
- Mantén `.env.example` actualizado cuando se añadan, renombren o retiren variables

## Integraciones externas

- Aísla llamadas a LLMs, APIs externas, ficheros o bases de datos detrás de servicios o clientes claros
- Define timeouts, reintentos y manejo de errores esperados para llamadas de red
- No mezcles construcción de prompts, llamada al proveedor y transformación de respuesta en una sola función grande
- Normaliza respuestas externas a DTOs internos antes de pasarlas al resto de la aplicación

## Observabilidad

- Usa logging estructurado o mensajes consistentes en puntos de entrada, errores esperados e integraciones externas
- Incluye contexto útil sin exponer secretos ni datos sensibles completos
- Evita `print()` en código de aplicación; resérvalo para scripts o ejemplos cuando sea aceptable
- Cuando añadas procesos largos, deja trazabilidad suficiente para diagnosticar fallos

## Seguridad

- Nunca escribas secretos, tokens, passwords o claves API en el código
- No registres información sensible en logs
- Valida entradas externas
- Usa consultas parametrizadas cuando haya acceso a bases de datos
- No incluyas transcripciones completas, prompts con datos sensibles o respuestas crudas de proveedores en logs
- Sanitiza datos que puedan acabar en prompts, rutas, consultas o mensajes de error

## Documentación

- Añade docstrings en APIs públicas o lógica no obvia
- Actualiza README o documentación si cambian comandos, configuración o comportamiento
- Mantén ejemplos y specs sincronizados con el comportamiento real
- Documenta decisiones no evidentes cerca del código que las necesita

## Validación final

- Ejecuta las pruebas más cercanas al cambio antes de terminar
- Para cambios de contratos, ejecuta también las pruebas de `tests/specs`
- Si no puedes ejecutar una validación relevante, deja indicado el motivo y el riesgo residual
