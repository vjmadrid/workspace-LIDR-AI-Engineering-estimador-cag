# ============================================
#  Makefile for Project Management
# ============================================

-include .env
export

# =====================
# Shell Configuration
# =====================

# Use bash as the default shell for executing commands
SHELL := /bin/bash

# =====================
# App Configuration
# =====================

# Main file to run the application
MAIN_FILE := app/main.py

# =====================
# Uvicorn Configuration
# =====================

# Uvicorn entry point for running the application
UVICORN_START_FILE := app.main:app
SERVICE_HOST ?= 0.0.0.0
SERVICE_PORT ?= 8000

# =====================
# Streamlit Configuration
# =====================

STREAMLIT_PORT ?= 8500

# =====================
# General Configuration
# =====================

# Commands
UV = uv
PYTHON = $(UV) run python
UVICORN = $(UV) run uvicorn

# =====================
# Pytest Configuration
# =====================

# Parameters for pytest execution
# -s: Disable output capture to see print statements and logs in real-time

PYTEST_PARAMETER_CONSOLE := -s

# Parameters for pytest execution
# --setup-show: Show setup and teardown of fixtures
PYTEST_PARAMETER_SETUP := --setup-show

PYTEST_PARAMETER_DEBUG := $(PYTEST_PARAMETER_CONSOLE)

# Parameters for pytest execution
# -ra: Show extra test summary info for skipped, failed, etc.
# -vv: Increase verbosity for more detailed test output
PYTEST_PARAMETER := -ra -vv $(PYTEST_PARAMETER_DEBUG)

# =====================
# Docker Configuration
# =====================

DOCKER_COMPOSE_FILE := docker-compose-2.yml

# =====================
# Help
# =====================

help: ## Show help message
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

# =====================
# Clean
# =====================

clean: ## Remove elements for build
	@rm -rf .venv
	@rm -rf .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .ruff_cache

# =====================
# Virtual Environment
# =====================

init-venv: ## Prepare Local Virtual Environment
	$(UV) venv

activate-venv: ## Activate the virtual environment
	@echo "To activate the virtual environment, run: source .venv/bin/activate"
	. .venv/bin/activate

verify-venv: ## Verify the virtual environment is active
	@echo "To verify the virtual environment is active, run: which python"
	which python


# =====================
# Dependencies
# =====================

sync-venv: ## Synchronise the virtual environment with the file pyproject.toml
	$(UV) sync

tree: ## Show dependency tree of packages
	$(UV) run python -m pipdeptree

tree-json: ## Show dependency tree of packages json
	$(UV) run python -m pipdeptree --json-tree

# =====================
# Installation
# =====================

install: ## Create the virtual environment and install dependencies
	$(UV) venv
	$(UV) sync

# =====================
# Execution
# =====================

run: ## Run Application
	$(PYTHON) -m app.main

run-script: ## Run a script: make run script=main.py
	PYTHONPATH=app $(UV) run $(script)

run-demo-openai: ## Run the OpenAI demo script
	PYTHONPATH=$(CURDIR) $(PYTHON) scripts/estimate_demo_openai.py

run-demo-anthropic: ## Run the Anthropic demo script
	PYTHONPATH=$(CURDIR) $(PYTHON) scripts/estimate_demo_anthropic.py

run-uvicorn: ## Run Application with Uvicorn
	$(UVICORN) $(UVICORN_START_FILE) --host $(SERVICE_HOST) --port $(SERVICE_PORT) --reload

run-streamlit: ## Run Streamlit application
	$(UV) run streamlit run front/streamlit/main_streamlit_openai.py --server.port $(STREAMLIT_PORT)

run-streamlit-2: ## Run Streamlit application 2
	$(UV) run streamlit run front/streamlit/main_streamlit_openai_2.py --server.port $(STREAMLIT_PORT)

run-streamlit-3: ## Run Streamlit application 3
	$(UV) run streamlit run front/streamlit/main_streamlit_openai_3.py --server.port $(STREAMLIT_PORT)

run-streamlit-client: ## Run Streamlit application
	$(UV) run streamlit run front/streamlit/main_streamlit_client_http.py --server.port $(STREAMLIT_PORT)


# =====================
# Linter
# =====================

lint: ## Run Ruff linter
	$(UV) run ruff check .


# =====================
# Formatter
# =====================

format: ## Run Ruff formatter
	$(UV) run ruff format .

fix: ## Run Ruff formatter with fixes
	$(UV) run ruff check . --fix
	$(UV) run ruff format .


# =====================
# Testing
# =====================

test: ## Run all tests of all types
	$(UV) run pytest $(PYTEST_PARAMETER) -v

test-units: ## Run unit tests with pytest
	$(UV) run pytest $(PYTEST_PARAMETER) tests/units

test-integrations: ## Run integration tests with pytest
	$(UV) run pytest $(PYTEST_PARAMETER) tests/integrations

test-lab: ## Run lab tests with pytest
	uv run pytest tests/units/app/services/openai/test_estimate_openai_services.py -q

test-specs: ## Run spec-driven tests
	$(CURDIR)/.venv/bin/python -m unittest discover -s tests

test-coverage: ## Run tests with coverage
	$(UV) run coverage --version
	$(UV) run coverage erase
	$(UV) run coverage run --include=app/* -m pytest -ra
	$(UV) run coverage report -m
	$(UV) run coverage html -d ./reports/coverage_html

# =====================
# Docker
# =====================

docker-build: ## Build the Docker image
	docker compose -f $(DOCKER_COMPOSE_FILE) build

docker-up: ## Start the application with Docker Compose
	docker compose -f $(DOCKER_COMPOSE_FILE) up --build

docker-down: ## Stop the application and remove containers
	docker compose -f $(DOCKER_COMPOSE_FILE) down

docker-logs: ## Follow the logs of the estimator service
	docker compose -f $(DOCKER_COMPOSE_FILE) logs -f estimator

docker-ps: ## Show the status of Docker containers
	docker compose -f $(DOCKER_COMPOSE_FILE) ps


# =====================
# Support
# =====================

kill-port-uvicorn: ## Kill any process using the service port
	$(CURDIR)/kill-port.sh $(SERVICE_PORT)

kill-port-streamlit: ## Kill any process using the Streamlit port
	$(CURDIR)/kill-port.sh $(STREAMLIT_PORT)



.DEFAULT_GOAL := help
