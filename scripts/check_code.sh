#!/usr/bin/env bash
set -euo pipefail

echo "Running code quality checks for fractalmusic"
echo

failed=0

run_check() {
    local name="$1"
    shift

    echo "Running ${name}..."
    if "$@"; then
        echo "${name} passed"
    else
        echo "${name} failed"
        failed=1
    fi
    echo
}

run_check "Ruff linting" ruff check fractalmusic tests
run_check "Ruff formatting" ruff format --check fractalmusic tests
run_check "Mypy type checking" mypy fractalmusic
run_check "Pytest with coverage" pytest
run_check "Bandit security check" bandit -r fractalmusic -c pyproject.toml

if [ "${failed}" -eq 0 ]; then
    echo "All checks passed"
    exit 0
fi

echo "Some checks failed"
exit 1
