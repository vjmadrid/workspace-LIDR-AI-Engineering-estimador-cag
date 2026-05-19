# estimador-cag

- [estimador-cag](#estimador-cag)
  - [Información general](#información-general)
  - [Stack Tecnológico](#stack-tecnológico)
    - [General](#general)
    - [Dependencias proyectos de arquitectura](#dependencias-proyectos-de-arquitectura)
    - [Dependencia de terceros](#dependencia-de-terceros)
  - [Pre-Requisitos](#pre-requisitos)
  - [Instalación](#instalación)
    - [Instalación de entorno virtual](#instalación-de-entorno-virtual)
    - [Instalación de dependencias](#instalación-de-dependencias)
  - [Uso](#uso)
    - [Problema "Address already in use"](#problema-address-already-in-use)
    - [Ejemplo de curl](#ejemplo-de-curl)
  - [Versionado](#versionado)
  - [Autores](#autores)


## Información general

Proyecto para controlar las estimaciones de los proyectos de un empresa, con el fin de mejorar la planificación y gestión de los recursos.

Para ello se harña uso de uan arquitectura CAG (Cache Augmente Generation)

## Stack Tecnológico

### General

* Python 3 (>=3.11) instalado
* uv instalado
* Soporte a Makefile
* Soporte a cURL
* Cuenta activa en OpenAI Platform y/ Anthropic Console con creditos disponibles
* API key de OpenAI y/o Anthropic como variables de entorno
* Docker y Docker Compose

### Dependencias proyectos de arquitectura

N/A

### Dependencia de terceros

**Desarrollo**

* **fastapi** : Framework web moderno y rápido para construir APIs con Python 3.6+ basado en estándares de Python type hints.
  * [Pypi](https://pypi.org/project/fastapi/)
  * [Repositorio](https://github.com/fastapi/fastapi)
  * [Documentacion](https://fastapi.tiangolo.com/)
  * [Web](https://fastapi.tiangolo.com/)
* **uvicorn[standard]** : Servidor ASGI para ejecutar aplicaciones web construidas con ciertos frameworks (ejemplo: FastAPI, Starlette, etc. )
  * [Pypi](https://pypi.org/project/uvicorn/)
  * [Repositorio](https://github.com/Kludex/uvicorn)
  * [Documentacion](https://uvicorn.dev/)
  * [Web](https://uvicorn.dev/)
* **openai** : Cliente oficial de OpenAI (SDK)
  * [Pypi](https://pypi.org/project/openai/)
  * [Repositorio](https://github.com/openai/openai-python)
  * [Documentacion](https://pypi.org/project/openai/)
  * [Web](https://pypi.org/project/openai/)
* **anthropic** : Cliente oficial de Anthropic (SDK)
  * [Pypi](https://pypi.org/project/anthropic/)
  * [Repositorio](https://github.com/anthropics/anthropic-sdk-python)
  * [Documentacion](https://github.com/anthropics/anthropic-sdk-python)
  * [Web](https://github.com/anthropics/anthropic-sdk-python)
* **streamlit** : Framework de código abierto para crear aplicaciones web interactivas y visualizaciones de datos con Python.
  * [Pypi](https://pypi.org/project/streamlit/)
  * [Repositorio](https://github.com/streamlit/streamlit)
  * [Documentacion](https://docs.streamlit.io/)
  * [Web](https://streamlit.io/)
* **python-dotenv** : Utilidad que facilita trabajar con ficheros de variables de entorno (.env)
  * [Pypi](https://pypi.org/project/python-dotenv/)
  * [Repositorio](https://github.com/theskumar/python-dotenv)
  * [Documentacion](https://saurabh-kumar.com/python-dotenv/)
  * [Web](https://saurabh-kumar.com/python-dotenv/)
* **pydantic-settings** : Utilidad que facilita trabajar con configuraciones basadas en Pydantic
  * [Pypi](https://pypi.org/project/pydantic-settings/)
  * [Repositorio](https://github.com/pydantic/pydantic-settings)
  * [Documentacion](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/)
  * [Web](https://pydantic.dev/docs/)
* **pipdeptree** : Utilidad de línea de domandos para mostrar el arbol de dependencias
  * [Pypi](https://pypi.org/project/pipdeptree/)
  * [Repositorio](https://github.com/naiquevin/pipdeptree)
  * [Documentacion](https://pypi.org/project/pipdeptree/)
* **tiktoken** : Utilidad para contar tokens en modelos de OpenAI
  * [Pypi](https://pypi.org/project/tiktoken/)
  * [Repositorio](https://github.com/openai/tiktoken)
  * [Documentacion](https://github.com/openai/tiktoken)
* **ruff** : Utilidad para analizar y formatear código Python
  * [Pypi](https://pypi.org/project/ruff/)
  * [Repositorio](https://github.com/astral-sh/ruff)
  * [Documentacion](https://docs.astral.sh/ruff/)
* **litellm** : Utilidad para interactuar con modelos de lenguaje de forma sencilla (Abstracción de LLMs)
  * [Pypi](https://pypi.org/project/litellm/)
  * [Repositorio](https://github.com/BerriAI/litellm)
  * [Documentacion](https://docs.litellm.ai/)
  * [Web](https://www.litellm.ai/)
* **httpx** : Cliente HTTP para Python, utilizado para realizar solicitudes HTTP de manera eficiente.
  * [Pypi](https://pypi.org/project/httpx/)
  * [Repositorio](https://github.com/encode/httpx)
  * [Documentacion](https://www.python-httpx.org/)
  * [Web](https://www.python-httpx.org/)
* **redis** : Cliente oficial de Redis para Python, utilizado para interactuar con bases de datos Redis.
  * [Pypi](https://pypi.org/project/redis/)
  * [Repositorio](https://github.com/redis/redis-py)
  * [Documentacion](https://redis-py.readthedocs.io/en/stable/)
  * [Web](https://github.com/redis/redis-py)
* **jinja2** : Motor de plantillas para Python, utilizado para generar texto dinámico a partir de plantillas.
  * [Pypi](https://pypi.org/project/Jinja2/)
  * [Repositorio](https://github.com/pallets/jinja/)
  * [Documentacion](https://jinja.palletsprojects.com/en/stable/)
  * [Web](https://jinja.palletsprojects.com/en/stable/)


**Testing / QA**

* **pytest** : Framework de testing para Python
  * [Pypi](https://pypi.org/project/pytest/)
  * [Repositorio](https://github.com/pytest-dev/pytest)
  * [Documentacion](https://docs.pytest.org/en/stable/)
* **pytest-cov** : Extensión de pytest que proporciona los datos de cobertura sobre los tests
  * [Pypi](https://pypi.org/project/pytest-cov/)
  * [Repositorio](https://github.com/pytest-dev/pytest-cov)
  * [Documentacion](https://pytest-cov.readthedocs.io/en/latest/)
* **pytest-randomly** : Extensión de pytest que permite ejecutar los tests en un orden aleatorio
  * [Pypi](https://pypi.org/project/pytest-randomly/)
  * [Repositorio](https://github.com/pytest-dev/pytest-randomly)
  * [Documentacion](https://github.com/pytest-dev/pytest-randomly)

## Pre-Requisitos

* Python 3 (>=3.11) instalado
* uv instalado
* cURL instalado
* Cuenta activa en OpenAI Platform y/ Anthropic Console con creditos disponibles
* API key de OpenAI y/o Anthropic como variables de entorno
* Docker y Docker Compose instalados

## Instalación

Pasos a seguir

* Arrancar un terminal
* Localizar el PATH de instalación (el lugar donde se encuentra el proyecto)

### Instalación de entorno virtual

Pasos a seguir:

* Ejecutar el siguiente comando para crear un entorno virtual

```bash
uv venv
```

* Activar el entorno virtual

```bash
source .venv/bin/activate
```

* Verificar que el entorno virtual esta activo

```bash
which python
```

* Verificar que se ha creado el entorno virtual como un directorio local en el proyecto llamado ".venv"


### Instalación de dependencias

Instalación de dependencias de forma manual

```bash
# General
uv add python-dotenv
uv add fastapi
uv add "uvicorn[standard]"
uv add openai
uv add anthropic
uv add pydantic-settings
uv add pipdeptree
uv add tiktoken
uv add streamlit
uv add litellm
uv add httpx
uv add redis
uv add jinja2

# Desarrollo
uv add --dev ruff
uv add --dev pytest
uv add --dev pytest-cov
uv add --dev pytest-randomly
```

## Uso

### Problema "Address already in use"

Pasos a seguir:

* Identificar el proceso que esta utilizando el puerto 8000

```bash
lsof -i :8000
```

* Matar el proceso identificado (reemplazar <PID> por el PID del proceso)

```bash
kill -9 <PID>
```

### Ejemplo de curl

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/estimate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "transcription": "El cliente solicita una aplicación móvil para gestionar reservas de salas de reuniones en una empresa. La app debe permitir a los empleados ver la disponibilidad, reservar, cancelar y recibir notificaciones. Se requiere autenticación corporativa, integración con el calendario de Outlook y panel de administración web para métricas."
}'
```

## Versionado

**Nota :** [SemVer](http://semver.org/) es utilizado por el versionado

Para ver las versiones disponibles ver los tags del repositorio

## Autores

* **Víctor Madrid**