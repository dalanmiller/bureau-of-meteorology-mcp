from __future__ import annotations

from mcp_bom_weather.clients.bom_client import BomClient
from mcp_bom_weather.config import SUPPORTED_CITIES
from mcp_bom_weather.tools.weather_tools import current_weather_all_major_cities


def test_all_cities_aggregated(examples_client: BomClient) -> None:
    items = current_weather_all_major_cities(client=examples_client)
    assert len(items) == len(SUPPORTED_CITIES)
    cities = [x["city"] for x in items]
    assert cities == SUPPORTED_CITIES
