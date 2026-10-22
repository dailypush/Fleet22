#!/bin/bash
# Refresh in a staging directory, then publish only after validation succeeds.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
    VENV_PYTHON="${PYTHON:-python3}"
fi
cd "$PROJECT_DIR"
exec "$VENV_PYTHON" -m scripts.update_all_data
