from __future__ import annotations

from collections.abc import Callable

from ..adapters.bom_adapter import (
    CurrentWeather,
    Forecast,
    parse_current_from_xml,
    parse_forecast_from_xml,
    parse_warnings_from_xml,
    validate_city,
)
from ..clients.bom_client import BomClient
from ..config import SUPPORTED_CITIES


def current_weather(city: str, *, client: BomClient | None = None) -> CurrentWeather:
    city = validate_city(city)
    client = client or BomClient()
    status, xml_text = client.fetch_city_xml(city)
    return parse_current_from_xml(city, status, xml_text)


def forecast(city: str, days: int = 7, *, client: BomClient | None = None) -> Forecast:
    city = validate_city(city)
    client = client or BomClient()
    status, xml_text = client.fetch_city_xml(city)
    return parse_forecast_from_xml(city, status, xml_text, days=days)


def current_weather_all_major_cities(*, client: BomClient | None = None) -> list[CurrentWeather]:
    client = client or BomClient()
    out: list[CurrentWeather] = []
    for c in SUPPORTED_CITIES:
        status, xml_text = client.fetch_city_xml(c)
        out.append(parse_current_from_xml(c, status, xml_text))
    return out


def current_warnings(*, client: BomClient | None = None) -> dict:
    client = client or BomClient()
    status, xml_text = client.fetch_warnings_xml()
    return parse_warnings_from_xml(status, xml_text)


ToolFn = Callable[..., object]

TOOLS: dict[str, ToolFn] = {
    "current_weather": current_weather,
    "forecast": forecast,
    "current_weather_all_major_cities": current_weather_all_major_cities,
    "current_warnings": current_warnings,
}
