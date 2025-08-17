from __future__ import annotations

from mcp_bom_weather.clients.bom_client import BomClient
from mcp_bom_weather.tools.weather_tools import current_warnings


def test_current_warnings_examples_client(examples_client: BomClient) -> None:  # type: ignore[no-redef]
    res = current_warnings(client=examples_client)
    assert isinstance(res, dict)
    assert "source" in res and res["source"] == "BoM"
    assert "count" in res and isinstance(res["count"], int)
