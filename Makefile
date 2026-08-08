SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTHON ?= python3.12
UV ?= uv
DEV_VENV := .venv
PI_VENV := .venv-pi
DEV_PYTHON := $(DEV_VENV)/bin/python
PI_PYTHON := $(PI_VENV)/bin/python
DEV_STAMP := $(DEV_VENV)/.flight-tracker-installed
PI_STAMP := $(PI_VENV)/.flight-tracker-installed
WEB_STAMP := src/frontend/node_modules/.flight-tracker-installed

.PHONY: help install install-pi dev pi stop status doctor test lint format \
	backend web device web-build

help: ## Show the available project commands
	@printf '%s\n' \
		'Flight Tracker development commands' \
		'' \
		'  make dev       Install missing dependencies and run API + web' \
		'  make pi        Build web and run API + web + e-paper client' \
		'  make stop      Stop a stack started by make dev or make pi' \
		'  make status    Show managed process status' \
		'  make doctor    Verify tools, managed processes, API, web, and proxy' \
		'  make test      Run Python tests/compilation and the frontend build' \
		'  make lint      Run Ruff, mypy, ESLint, and TypeScript checks' \
		'  make format    Apply Ruff and frontend ESLint fixes' \
		'  make install   Install laptop backend/tooling and web dependencies' \
		'  make install-pi Install the isolated Raspberry Pi runtime'

install: $(DEV_STAMP) $(WEB_STAMP) ## Install laptop development dependencies

$(DEV_STAMP): src/backend/requirements.txt apps/api/requirements-dev.txt
	@command -v $(UV) >/dev/null || { echo 'uv is required: https://docs.astral.sh/uv/'; exit 1; }
	@command -v $(PYTHON) >/dev/null || { echo 'Python 3.12+ is required'; exit 1; }
	@test -x $(DEV_PYTHON) || $(UV) venv --python $(PYTHON) $(DEV_VENV)
	@$(UV) pip install --python $(DEV_PYTHON) \
		-r src/backend/requirements.txt \
		-r apps/api/requirements-dev.txt
	@touch $(DEV_STAMP)

$(WEB_STAMP): src/frontend/package.json src/frontend/package-lock.json
	@command -v npm >/dev/null || { echo 'Node.js and npm are required'; exit 1; }
	@npm ci --prefix src/frontend
	@touch $(WEB_STAMP)

install-pi: $(PI_STAMP) $(WEB_STAMP) ## Install Pi runtime and web dependencies

$(PI_STAMP): src/backend/requirements.txt src/raspi/requirements.txt
	@command -v $(UV) >/dev/null || { echo 'uv is required: https://docs.astral.sh/uv/'; exit 1; }
	@command -v $(PYTHON) >/dev/null || { echo 'Python 3.12+ is required'; exit 1; }
	@test -x $(PI_PYTHON) || $(UV) venv --python $(PYTHON) --system-site-packages $(PI_VENV)
	@$(UV) pip install --python $(PI_PYTHON) \
		-r src/backend/requirements.txt \
		-r src/raspi/requirements.txt
	@touch $(PI_STAMP)

dev: install ## Run the local API and Vite development server
	@$(PYTHON) scripts/run_stack.py dev --python $(DEV_PYTHON)

pi: install-pi web-build ## Run the production-style Raspberry Pi stack
	@$(PYTHON) scripts/run_stack.py pi --python $(PI_PYTHON)

stop: ## Stop managed local or Pi processes
	@$(PYTHON) scripts/run_stack.py stop

status: ## Show managed process status
	@$(PYTHON) scripts/run_stack.py status

doctor: ## Verify local tools and the running development stack
	@$(PYTHON) scripts/run_stack.py doctor --python $(DEV_PYTHON)

test: install install-pi ## Run backend, device simulator, and frontend verification
	@cd apps/api && ../../$(DEV_PYTHON) -m unittest discover -s tests -v
	@cd src/backend && ../../$(DEV_PYTHON) -m unittest discover -s tests -v
	@cd src/raspi && ../../$(PI_PYTHON) -m unittest discover -s tests -v
	@$(DEV_PYTHON) -m compileall -q apps/api/flight_tracker src/backend src/raspi
	@npm --prefix src/frontend run build

lint: install ## Run Python and TypeScript quality checks
	@$(DEV_PYTHON) -m ruff check apps/api/flight_tracker apps/api/tests scripts/run_stack.py
	@cd apps/api && ../../$(DEV_PYTHON) -m mypy flight_tracker
	@npm --prefix src/frontend run lint
	@npm --prefix src/frontend run typecheck

format: install ## Apply available Python and frontend fixes
	@$(DEV_PYTHON) -m ruff format apps/api/flight_tracker apps/api/tests scripts/run_stack.py
	@$(DEV_PYTHON) -m ruff check --fix --exit-zero \
		apps/api/flight_tracker apps/api/tests scripts/run_stack.py
	@npm --prefix src/frontend run lint -- --fix

backend: $(DEV_STAMP) ## Run only the local API
	@mkdir -p .state
	@test -f .state/backend.toml || cp src/backend/config.toml .state/backend.toml
	@cd src/backend && FLIGHT_TRACKER_CONFIG_FILE=../../.state/backend.toml \
		../../$(DEV_PYTHON) -m uvicorn main:app \
		--host 0.0.0.0 --port 8000 --reload

web: $(WEB_STAMP) ## Run only the Vite development server
	@npm --prefix src/frontend run dev -- --host 0.0.0.0

device: $(PI_STAMP) ## Run only the Raspberry Pi display client
	@cd src/raspi && ../../$(PI_PYTHON) agent.py

web-build: $(WEB_STAMP) ## Build the web application for production-style serving
	@npm --prefix src/frontend run build
