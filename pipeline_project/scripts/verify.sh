#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PY="$ROOT_DIR/.venv/bin/python"

echo "Using Python: $VENV_PY"

# run migrations in a temporary sqlite DB (default settings use file db, but tests use memory)
$VENV_PY "$ROOT_DIR/manage.py" migrate --noinput

# run tests
$VENV_PY "$ROOT_DIR/manage.py" test -v2

echo "Verification complete."
