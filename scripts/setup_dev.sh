#!/usr/bin/env bash
set -euo pipefail

echo "Setting up development environment for fractalmusic"

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required. Install uv, then rerun this script."
    exit 1
fi

uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

pre-commit install
pre-commit install --hook-type pre-push

echo
echo "Development environment is ready."
echo "Activate it with: source .venv/bin/activate"
