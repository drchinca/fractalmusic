#!/usr/bin/env bash
set -euo pipefail

coverage=true
pytest_args=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-cov)
            coverage=false
            shift
            ;;
        -v|--verbose)
            pytest_args+=("-vv")
            shift
            ;;
        *)
            pytest_args+=("$1")
            shift
            ;;
    esac
done

echo "Running tests for fractalmusic"
echo

if [ "${coverage}" = true ]; then
    pytest "${pytest_args[@]}"
    echo
    echo "Coverage reports generated in htmlcov/ and coverage.xml"
else
    pytest --no-cov "${pytest_args[@]}"
fi
