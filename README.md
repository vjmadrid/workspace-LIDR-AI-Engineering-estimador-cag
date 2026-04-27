# estimador-cag

- [estimador-cag](#estimador-cag)
  - [Información general](#información-general)
  - [Stack Tecnológico](#stack-tecnológico)
    - [General](#general)
    - [Dependencias proyectos de arquitectura](#dependencias-proyectos-de-arquitectura)
    - [Dependencias de terceros](#dependencias-de-terceros)
  - [Pre-Requisitos](#pre-requisitos)
  - [Instalación](#instalación)
    - [Instalación de entorno virtual](#instalación-de-entorno-virtual)
    - [Instalación de dependencias](#instalación-de-dependencias)
  - [Versionado](#versionado)
  - [Autores](#autores)


## Información general

Proyecto para controlar las estimaciones de los proyectos de un empresa, con el fin de mejorar la planificación y gestión de los recursos.

Para ello se harña uso de uan arquitectura CAG (Cache Augmente Generation)

## Stack Tecnológico

* Python 3 (>=3.11) instalado
* uv instalado
* Soporte a Makefile
* Cuenta activa en OpenAI Platform y/ Anthropic Console con creditos disponibles
* API key de OpenAI y/o Anthropic como variables de entorno

### General

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

### Dependencias proyectos de arquitectura

N/A

### Dependencias de terceros

* **python-dotenv** : Utilidad que facilita trabajar con ficheros de variables de entorno (.env)
  * [Pypi](https://pypi.org/project/python-dotenv/)
  * [Repositorio](https://github.com/theskumar/python-dotenv)
  * [Documentacion](https://saurabh-kumar.com/python-dotenv/)
  * [Web](https://saurabh-kumar.com/python-dotenv/)

## Pre-Requisitos

* Python 3 (>=3.11) instalado
* uv instalado
* Cuenta activa en OpenAI Platform y/ Anthropic Console con creditos disponibles
* API key de OpenAI y/o Anthropic como variables de entorno

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
uv add python-dotenv
uv add fastapi
uv add "uvicorn[standard]"
uv add openai
uv add anthropic
```

## Versionado

**Nota :** [SemVer](http://semver.org/) es utilizado por el versionado

Para ver las versiones disponibles ver los tags del repositorio

## Autores

* **Víctor Madrid**