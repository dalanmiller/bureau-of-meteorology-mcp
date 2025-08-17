from __future__ import annotations

import re

import pytest

from mcp_bom_weather.clients.bom_client import BomClient
from mcp_bom_weather.config import SUPPORTED_CITIES
from mcp_bom_weather.tools.weather_tools import current_weather


@pytest.mark.parametrize("city", SUPPORTED_CITIES)
def test_current_weather_shape(city: str, examples_client: BomClient) -> None:
    cw = current_weather(city, client=examples_client)
    assert cw["city"] == city
    assert isinstance(cw["temp_c"], int | float)
    assert isinstance(cw["condition"], str)
    assert re.match(r"^\d{4}-\d{2}-\d{2}T", cw["updated_at"])  # ISO start
