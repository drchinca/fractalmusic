.PHONY: help install dev-install test test-quick check format clean lint type-check pre-commit build

UV_RUN := uv run --extra dev

help:
	@echo "fractalmusic - available commands:"
	@echo "  make install       Install production dependencies"
	@echo "  make dev-install   Install development dependencies and hooks"
	@echo "  make test          Run tests with coverage"
	@echo "  make test-quick    Run tests without coverage"
	@echo "  make check         Run lint, format, type, test, and security checks"
	@echo "  make format        Format code with Ruff"
	@echo "  make lint          Lint code with Ruff"
	@echo "  make type-check    Run Mypy"
	@echo "  make build         Build package distributions"
	@echo "  make clean         Remove generated artifacts"

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
