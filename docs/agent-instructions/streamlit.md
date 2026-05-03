# Instrucciones para desarrollo Streamlit

Estas instrucciones aplican al código dentro de `app/`.

## Objetivo

La aplicación Streamlit debe ser clara para el usuario, robusta ante errores y mantenible a nivel de código.

Estas reglas aplican cuando exista o se modifique una UI Streamlit. Si la tarea solo afecta al backend FastAPI, no introduzcas dependencias o estructura de Streamlit sin necesidad.

## Diseño de la app

- Mantén la lógica de UI separada de la lógica de negocio.
- Evita poner toda la aplicación en un único fichero si crece demasiado.
- Extrae funciones para carga de datos, transformación, validación y renderizado.
- Usa nombres de páginas, secciones y controles comprensibles.
- Prioriza una experiencia simple y guiada para el usuario.
- Mantén la primera pantalla orientada a la tarea principal, no a una explicación larga.
- Evita mezclar llamadas HTTP, parsing, cálculo y renderizado en el mismo bloque.
- Usa componentes nativos de Streamlit antes de añadir librerías UI externas.
- Mantén textos de ayuda breves y accionables; no muestres detalles técnicos salvo que sean útiles.
- Diseña estados vacíos, errores y resultados parciales como parte del flujo normal.

## Estado

- Usa `st.session_state` de forma explícita y documentada.
- Inicializa claves de session state antes de usarlas.
- Evita depender de estado global mutable fuera de Streamlit.
- No guardes secretos ni información sensible en `session_state` si no es necesario.
- Agrupa claves relacionadas con prefijos consistentes para evitar colisiones.
- Limpia o reinicia estado cuando cambie una entrada que invalide resultados previos.
- No uses `session_state` como sustituto de modelos de datos claros.
- Evita guardar respuestas completas de proveedores si contienen datos sensibles o son demasiado grandes.

## Rendimiento

- Usa `st.cache_data` para datos calculados o cargados.
- Usa `st.cache_resource` para clientes, conexiones o recursos pesados.
- Define correctamente parámetros de caché, invalidación y TTL cuando aplique.
- Evita recalcular operaciones caras en cada rerun.
- No cachees datos dependientes de usuario sin incluir los parámetros relevantes en la clave.
- Evita cachear secretos, tokens o resultados sensibles compartibles entre sesiones.
- Mide o acota operaciones lentas antes de optimizar con caché.
- Usa placeholders o contenedores para actualizar resultados sin redibujar una pantalla confusa.

## Datos

- Valida ficheros subidos por el usuario.
- Maneja datos vacíos, columnas ausentes y formatos incorrectos.
- Muestra mensajes de error accionables, no trazas internas.
- No asumas que los datos siempre tienen el formato esperado.
- Limita tamaño y tipo de ficheros cuando uses uploaders.
- Normaliza datos antes de pasarlos al backend o a servicios de cálculo.
- Muestra unidades, monedas, fechas y rangos con formato consistente.
- Evita exponer datos crudos si contienen información personal o confidencial.

## UI

- Usa `st.form` cuando haya varios inputs que deban enviarse juntos.
- Usa `st.spinner` para operaciones lentas.
- Usa `st.warning`, `st.error`, `st.success` e `st.info` de forma clara.
- Evita pantallas saturadas; agrupa contenido con tabs, expanders o columnas cuando ayude.
- Muestra resultados intermedios solo si aportan valor.
- Deshabilita botones mientras falten entradas obligatorias o muestra validaciones claras.
- Prefiere controles específicos (`selectbox`, `number_input`, `date_input`, `slider`) antes que texto libre cuando el dominio sea cerrado.
- No ocultes acciones principales dentro de expanders.
- Mantén tablas y métricas legibles en pantallas estrechas.
- Usa `st.download_button` para resultados exportables cuando aporte valor al flujo.
- Evita duplicar información entre texto, métricas y tablas si no mejora la decisión del usuario.

## Integración con backend

- Aísla llamadas HTTP o SDKs externos en módulos propios.
- Configura URLs, tokens y timeouts mediante configuración.
- Maneja timeouts, errores de red y respuestas inválidas.
- No bloquees la UI sin feedback al usuario.
- Define contratos claros entre UI y backend usando modelos o funciones adaptadoras.
- Convierte errores del backend en mensajes comprensibles para usuario final.
- No llames directamente a servicios internos del backend si la UI debe comportarse como cliente externo.
- Mantén URL base, timeouts y credenciales fuera del código de UI.
- Reintenta solo operaciones idempotentes o cuando el usuario entienda el efecto.

## Seguridad

- Lee secretos desde `st.secrets`, variables de entorno o configuración segura.
- Nunca hardcodees API keys, passwords o tokens.
- No muestres información sensible en errores, logs o componentes UI.
- Sanitiza o valida entradas antes de usarlas en consultas, rutas o prompts.
- No guardes secretos en parámetros de URL ni en estado descargable.
- Evita renderizar HTML inseguro; si usas `unsafe_allow_html`, justifica y limita el contenido.
- Redacta o resume transcripciones y prompts antes de mostrarlos si pueden contener datos sensibles.
- Respeta límites de autorización del backend; la UI no sustituye controles del servidor.

## Accesibilidad y usabilidad

- Usa etiquetas claras en inputs y botones; evita depender solo de iconos o posición.
- Proporciona mensajes de error cerca de la acción que los provocó.
- Mantén contraste suficiente y no comuniques estados solo con color.
- Usa orden visual estable para que los reruns no desorienten al usuario.
- Evita textos largos en columnas estrechas; usa secciones o expanders cuando mejore la lectura.

## Testing

- Testea funciones de negocio fuera de Streamlit con pytest.
- Mantén la mayor parte de la lógica testeable sin arrancar la UI.
- Añade tests para transformaciones de datos y validaciones.
- Prueba adaptadores de backend con mocks de respuestas HTTP.
- Añade tests para serialización/deserialización si la UI consume contratos de API.
- Extrae funciones puras para cálculos, parsing y formateo antes de añadir tests.
- Si hay flujos críticos, valida manualmente la UI en navegador además de ejecutar tests.

## Validación final

Antes de terminar cambios en Streamlit, intenta ejecutar:

```bash
pytest
ruff check .
```

Si la UI puede arrancarse localmente, comprueba al menos el flujo principal con datos válidos y un caso de error.
