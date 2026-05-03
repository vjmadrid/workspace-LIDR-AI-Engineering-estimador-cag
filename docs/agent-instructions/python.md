# Instrucciones generales de desarrollo Python

## Objetivo

Este repositorio debe mantenerse con código Python claro, tipado, testeable y fácil de mantener.

## Estilo de código

- Usa Python 3.11+ salvo que el proyecto indique otra versión
- Escribe código simple y explícito antes que soluciones demasiado abstractas
- Usa nombres descriptivos para funciones, variables, clases y módulos
- Mantén las funciones pequeñas y con una única responsabilidad
- Evita lógica compleja en el nivel superior de los módulos
- No introduzcas dependencias nuevas sin justificarlo
- No dupliques lógica: extrae funciones o servicios reutilizables cuando tenga sentido
- Prefiere retornos tempranos para reducir anidación cuando mejoren la legibilidad
- Evita flags booleanos que cambien demasiado el comportamiento de una función; separa funciones si hay dos casos de uso claros
- Mantén imports ordenados y elimina código muerto al tocar un módulo
- Usa `pathlib.Path` para rutas de ficheros en lugar de concatenar strings
- Evita valores mágicos: extrae constantes con nombre cuando el significado no sea obvio
- No hagas trabajo pesado en import time; deja inicialización costosa para factories, funciones o dependencias

## Tipado

- Añade type hints en funciones públicas, métodos y estructuras relevantes.
- Prefiere `list[str]`, `dict[str, Any]`, `Path`, `Sequence`, `Mapping`, etc.
- Evita `Any` salvo que sea inevitable.
- Usa `TypedDict`, `dataclass` o modelos Pydantic cuando ayuden a clarificar estructuras.
- Usa `Optional[T]` o `T | None` solo cuando `None` sea un estado válido y manejado
- Prefiere `Sequence` o `Mapping` en parámetros cuando no necesites mutabilidad
- Evita casts para silenciar el type checker; mejora el modelo de datos cuando sea posible
- Anota retornos de funciones públicas, helpers compartidos y métodos de servicios
- No uses diccionarios anónimos para estructuras complejas que crucen capas; usa DTOs, dataclasses o modelos

## Gestión de errores

- No ocultes excepciones con `except Exception` salvo que haya una razón clara.
- Cuando captures errores, añade contexto útil
- No uses `print()` para errores de aplicación; usa logging
- Falla pronto cuando una configuración obligatoria no exista
- Define excepciones específicas del dominio cuando ayuden a distinguir errores esperados
- Encapsula errores de proveedores externos en errores propios antes de exponerlos a capas superiores
- No devuelvas `None` para representar fallos si el llamador no puede actuar con claridad
- Incluye mensajes útiles para operación y debugging, sin filtrar secretos o datos sensibles
- Mantén el stack trace original con `raise ... from exc` cuando transformes excepciones

## Testing

- Añade o actualiza tests cuando cambie comportamiento
- Usa pytest como framework preferente
- Los tests deben cubrir casos normales, límites y errores relevantes
- Evita tests frágiles dependientes de orden, tiempo o servicios externos
- Usa fixtures para preparación reutilizable
- Mantén tests unitarios cerca de la lógica y tests de contrato en `tests/specs` cuando afecten specs
- Mockea red, LLMs, reloj y aleatoriedad para que los tests sean deterministas
- Usa nombres de test que describan comportamiento observable, no detalles internos
- Añade tests de regresión para cada bug corregido
- Evita aserciones demasiado amplias sobre snapshots completos si solo importa una parte del resultado
- Cubre casos vacíos, límites de longitud, entradas inválidas y errores de proveedor cuando apliquen

## Datos y modelos

- Valida datos en los bordes del sistema y trabaja con estructuras confiables dentro de los servicios
- Mantén modelos de request/response separados de DTOs internos si evolucionan a ritmos distintos
- Evita mutar argumentos recibidos salvo que el nombre y la documentación lo hagan explícito
- Usa enums o literales cuando un campo solo admita un conjunto cerrado de valores
- Normaliza unidades, monedas, porcentajes y tokens en una capa clara antes de calcular con ellos

## Integraciones y configuración

- Lee configuración desde `app/config.py` o el mecanismo central del proyecto
- Inyecta clientes externos en servicios cuando eso facilite tests o sustitución
- Define timeouts para llamadas de red y maneja respuestas inválidas de forma explícita
- No instancies clientes costosos en cada llamada si pueden reutilizarse de forma segura
- No hardcodees modelos, endpoints o costes si ya existe un módulo de constantes o configuración adecuado

## Logging

- Usa `logging.getLogger(__name__)` en módulos de aplicación
- Registra eventos relevantes con contexto mínimo suficiente
- No registres transcripciones completas, prompts con datos sensibles, tokens o claves
- Usa niveles de log coherentes: `debug` para detalle, `info` para eventos relevantes, `warning` para degradaciones y `error` para fallos

## Calidad

Antes de considerar terminada una tarea, intenta ejecutar:

```bash
pytest
ruff check .
ruff format --check .
mypy .
```

Si el proyecto no tiene alguna herramienta configurada o no puede ejecutarse por dependencias externas, indica qué comando falló y por qué.
