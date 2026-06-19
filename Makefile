.PHONY: help install dev-install test test-quick smoke check format clean lint type-check pre-commit build \
        bff bff-install bff-test web web-install web-build chat chat-stop

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
	@echo "    make format        Format code with Ruff"
	@echo "    make lint          Lint code with Ruff"
	@echo "    make type-check    Run Mypy"
	@echo "    make build         Build package distributions"
	@echo "    make clean         Remove generated artifacts"
	@echo ""
	@echo "  Chat — backend (chat_bff/) and frontend (web/):"
	@echo "    make chat          Start BFF (:8002) AND web dev server (:5174)"
	@echo "    make chat-stop     Kill anything bound to :8002 / :5174"
	@echo "    make bff           Start the chat BFF on :8002 (foreground)"
	@echo "    make web           Start the Vite dev server on :5174 (foreground)"
	@echo "    make bff-install   uv-install chat_bff in editable mode"
	@echo "    make web-install   npm install in web/"
	@echo "    make web-build     Build the web app for production"
	@echo "    make bff-test      Run chat_bff pytest suite"

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

# ----- chat-v1 dev commands -----

BFF_PORT ?= 8002
WEB_PORT ?= 5174
CHAT_LOG_DIR := /tmp/fractalmusic-chat

bff-install:
	cd chat_bff && uv pip install -e ".[dev]"

bff-test:
	cd chat_bff && uv run pytest

bff:
	cd chat_bff && uv run uvicorn 'chat_bff.bootstrap:app_factory' --factory \
	    --host 127.0.0.1 --port $(BFF_PORT) --reload

web-install:
	cd web && npm install

web-build:
	cd web && npm run build

web:
	cd web && npm run dev -- --port $(WEB_PORT) --strictPort

# Start both BFF and web in the background, tail their logs together.
# The handler kills both on Ctrl-C. Logs persist at $(CHAT_LOG_DIR)/*.log.
chat:
	@mkdir -p $(CHAT_LOG_DIR)
	@echo "→ chat_bff   :$(BFF_PORT)   logs: $(CHAT_LOG_DIR)/bff.log"
	@echo "→ web (vite) :$(WEB_PORT)  logs: $(CHAT_LOG_DIR)/web.log"
	@echo "→ open http://localhost:$(WEB_PORT)/#chat"
	@echo "→ Ctrl-C stops both."
	@trap 'echo; echo "stopping..."; kill 0' INT TERM EXIT; \
	(cd chat_bff && uv run uvicorn 'chat_bff.bootstrap:app_factory' --factory \
	    --host 127.0.0.1 --port $(BFF_PORT) --reload \
	    > $(CHAT_LOG_DIR)/bff.log 2>&1) & \
	(cd web && npm run dev -- --port $(WEB_PORT) --strictPort \
	    > $(CHAT_LOG_DIR)/web.log 2>&1) & \
	tail -f $(CHAT_LOG_DIR)/bff.log $(CHAT_LOG_DIR)/web.log

chat-stop:
	@echo "killing anything bound to :$(BFF_PORT) and :$(WEB_PORT)..."
	@-lsof -ti :$(BFF_PORT) | xargs -r kill -9 2>/dev/null || true
	@-lsof -ti :$(WEB_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "done."
