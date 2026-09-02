.PHONY: help install dev-install test test-quick smoke check verify format clean lint type-check pre-commit build \
        api api-install api-test web web-install web-build dev dev-stop

UV_RUN := uv run --extra dev

help:
	@echo "fractalmusic - available commands:"
	@echo ""
	@echo "  Python core (fractalmusic/):"
	@echo "    make install       Install production dependencies"
	@echo "    make dev-install   Install development dependencies and hooks"
	@echo "    make test          Run tests with coverage"
	@echo "    make test-quick    Run tests without coverage"
	@echo "    make smoke         Generate WAV + Strudel smoke artifacts"
	@echo "    make check         Run lint, format, type, test, and security checks"
	@echo "    make verify        Run full local merge gate: core, API, and web"
	@echo "    make format        Format code with Ruff"
	@echo "    make lint          Lint code with Ruff"
	@echo "    make type-check    Run Mypy"
	@echo "    make build         Build package distributions"
	@echo "    make clean         Remove generated artifacts"
	@echo ""
	@echo "  Engine API (gatople_api/) and web app (web/):"
	@echo "    make dev           Start gatople_api (:8002) AND web dev server (:5174)"
	@echo "    make dev-stop      Kill anything bound to :8002 / :5174"
	@echo "    make api           Start gatople_api on :8002 (foreground)"
	@echo "    make web           Start the Vite dev server on :5174 (foreground)"
	@echo "    make api-install   uv-install gatople_api in editable mode"
	@echo "    make web-install   npm install in web/"
	@echo "    make web-build     Build the web app for production"
	@echo "    make api-test      Run gatople_api pytest suite"

install:
	uv pip install -e .

dev-install:
	uv pip install -e ".[dev]"
	pre-commit install
	pre-commit install --hook-type pre-push

test:
	$(UV_RUN) bash scripts/test.sh

test-quick:
	$(UV_RUN) bash scripts/test.sh --no-cov

smoke:
	$(UV_RUN) pytest --no-cov -m smoke tests/smoke

check:
	$(UV_RUN) bash scripts/check_code.sh

verify:
	$(MAKE) check
	$(MAKE) api-test
	cd web && npm run lint
	cd web && npm run build

format:
	$(UV_RUN) ruff format fractalmusic tests
	$(UV_RUN) ruff check --fix fractalmusic tests

lint:
	$(UV_RUN) ruff check fractalmusic tests

type-check:
	$(UV_RUN) mypy fractalmusic

pre-commit:
	$(UV_RUN) pre-commit run --all-files

build:
	$(UV_RUN) python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# ----- gatople_api + web dev commands -----

API_PORT ?= 8002
WEB_PORT ?= 5174
DEV_LOG_DIR := /tmp/fractalmusic-dev

api-install:
	cd gatople_api && uv pip install -e ".[dev]"

api-test:
	cd gatople_api && uv run pytest

api:
	cd gatople_api && uv run uvicorn 'gatople_api.bootstrap:app_factory' --factory \
	    --host 127.0.0.1 --port $(API_PORT) --reload

web-install:
	cd web && npm install

web-build:
	cd web && npm run build

web:
	cd web && npm run dev -- --port $(WEB_PORT) --strictPort

# Start both the engine API and web in the background, tail their logs together.
# The handler kills both on Ctrl-C. Logs persist at $(DEV_LOG_DIR)/*.log.
dev:
	@mkdir -p $(DEV_LOG_DIR)
	@echo "→ gatople_api :$(API_PORT)   logs: $(DEV_LOG_DIR)/api.log"
	@echo "→ web (vite)  :$(WEB_PORT)  logs: $(DEV_LOG_DIR)/web.log"
	@echo "→ open http://localhost:$(WEB_PORT)/#chat"
	@echo "→ Ctrl-C stops both."
	@trap 'echo; echo "stopping..."; kill 0' INT TERM EXIT; \
	(cd gatople_api && uv run uvicorn 'gatople_api.bootstrap:app_factory' --factory \
	    --host 127.0.0.1 --port $(API_PORT) --reload \
	    > $(DEV_LOG_DIR)/api.log 2>&1) & \
	(cd web && npm run dev -- --port $(WEB_PORT) --strictPort \
	    > $(DEV_LOG_DIR)/web.log 2>&1) & \
	tail -f $(DEV_LOG_DIR)/api.log $(DEV_LOG_DIR)/web.log

dev-stop:
	@echo "killing anything bound to :$(API_PORT) and :$(WEB_PORT)..."
	@-lsof -ti :$(API_PORT) | xargs -r kill -9 2>/dev/null || true
	@-lsof -ti :$(WEB_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "done."
