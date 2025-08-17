#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  if [[ "${1-}" == "--http"* || "${1-}" == "--stdio"* || $# -gt 0 ]]; then
    exec uv run -q python -m mcp_bom_weather.fast_mcp_server "$@"
  else
    exec uv run -q python -m mcp_bom_weather.fast_mcp_server --stdio
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -d "$ROOT_DIR/.venv" ]; then
  # shellcheck disable=SC1091
  . "$ROOT_DIR/.venv/bin/activate"
fi
export PYTHONPATH="$ROOT_DIR/src:${PYTHONPATH:-}"
exec python -m mcp_bom_weather.fast_mcp_server "$@"

