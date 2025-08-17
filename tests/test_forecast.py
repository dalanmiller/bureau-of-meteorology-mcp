from __future__ import annotations

import pytest

from mcp_bom_weather.clients.bom_client import BomClient
from mcp_bom_weather.config import SUPPORTED_CITIES
from mcp_bom_weather.tools.weather_tools import forecast

DAYS = 3


@pytest.mark.parametrize("city", SUPPORTED_CITIES)
def test_forecast_days(city: str, examples_client: BomClient) -> None:
    fc = forecast(city, days=DAYS, client=examples_client)
    assert fc["city"] == city
    assert len(fc["days"]) == DAYS
    for day in fc["days"]:
        assert set(day.keys()) == {"date", "min_c", "max_c", "condition"}
