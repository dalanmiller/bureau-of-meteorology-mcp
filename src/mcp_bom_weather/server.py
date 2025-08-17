from __future__ import annotations

import json
from typing import Any

from .tools.weather_tools import TOOLS


def register_tools() -> dict[str, Any]:
    """Return a mapping of tool name -> callable.

    This is a simple stand-in for integrating with an actual MCP server runtime.
    """
    return dict(TOOLS)


def main(argv: list[str] | None = None) -> None:
    tools = register_tools()
    summary = {
        "tools": sorted(list(tools.keys())),
        "usage": {
            "current_weather": "python -m mcp_bom_weather.server",
            "forecast": "python -m mcp_bom_weather.server",
        },
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
