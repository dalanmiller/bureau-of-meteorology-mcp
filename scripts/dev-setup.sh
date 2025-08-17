#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  uv sync
else
  echo "uv not found; falling back to pip" >&2
  python -m venv .venv
  . .venv/bin/activate
  pip install -e .[dev]
fi

ruff check --fix || true
ruff format || true
echo "Dev setup complete."

