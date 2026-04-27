# ============================================
#  Makefile for Project Management
# ============================================

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

# =====================
# General Configuration
# =====================

# Commands
UV = uv
PYTHON = $(UV) run python
UVICORN = uvicorn

# =====================
# Help
# =====================

help: ## Show help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# =====================
# Clean
# =====================

clean: ## Remove elements for build
	rm -rf .venv
	rm -rf .pytest_cache

# =====================
# Virtual Environment
# =====================

init-venv: ## Prepare Local Virtual Environment
	$(UV) venv

# =====================
# Dependencies
# =====================

sync-venv: ## Synchronise the virtual environment with the file pyproject.toml
	$(UV) sync

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
	$(UV) run $(script)

run-uvicorn: ## Run Application with Uvicorn
	$(UVICORN) $(UVICORN_START_FILE) --reload

.DEFAULT_GOAL := help