# Contributing to fractalmusic

## Development Setup

Install dependencies and hooks:

```bash
bash scripts/setup_dev.sh
source .venv/bin/activate
```

Or run commands through uv without activating the environment:

```bash
uv run --extra dev pytest
uv run --extra dev ruff check fractalmusic tests
```

## Quality Gates

Run the full local check before submitting changes:

```bash
make check
```

The check includes Ruff linting, Ruff formatting, Mypy, pytest with coverage,
and Bandit.

## Code Style

- Keep Python formatted with Ruff.
- Add type hints for public functions and non-obvious private helpers.
- Keep tests close to behavior: unit tests for isolated rules, integration
  tests for cross-module behavior, and UAT tests for Gherkin scenarios.
- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`,
  and `chore:`.

## Useful Commands

```bash
make format
make lint
make type-check
make test
make test-quick
make build
make clean
```
