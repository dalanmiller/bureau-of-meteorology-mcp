from __future__ import annotations

import argparse
from typing import Any

from .adapters.bom_adapter import CurrentWeather, Forecast

try:
    # Use FastMCP from the official python-sdk
    from mcp.server.fastmcp import FastMCP
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "The 'mcp' python-sdk is required. Install with "
        '`uv add "mcp[cli]"` or `pip install "mcp[cli]"`.'
    ) from e

from .tools import weather_tools as tools

mcp = FastMCP("mcp-bom-weather")


@mcp.tool()
def current_weather(city: str) -> CurrentWeather:
    return tools.current_weather(city)


@mcp.tool()
def forecast(city: str, days: int = 7) -> Forecast:
    return tools.forecast(city, days=days)


@mcp.tool()
def current_weather_all_major_cities() -> list[CurrentWeather]:
    return tools.current_weather_all_major_cities()


@mcp.tool()
def current_warnings() -> dict[str, Any]:
    return tools.current_warnings()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("mcp-bom-weather (FastMCP)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--stdio", action="store_true", help="Run with stdio transport")
    group.add_argument("--http", action="store_true", help="Run Streamable HTTP transport")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP host")
    parser.add_argument("--port", type=int, default=4242, help="HTTP port")
    args = parser.parse_args()

    if args.http:
        # Configure host/port then run streamable HTTP directly via FastMCP
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="streamable-http")
    else:
        # Default to stdio
        mcp.run()
