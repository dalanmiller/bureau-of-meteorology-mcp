from __future__ import annotations

from typing import Literal as _PyLiteral

try:  # Prefer Astral 'ty' Literal if available
    from ty import Literal as _TyLiteral  # type: ignore

    _Literal = _TyLiteral
except Exception:  # pragma: no cover
    _Literal = _PyLiteral

from ..adapters.bom_adapter import CurrentWeather, Forecast, ForecastDay

CityLiteral = _Literal[
    "Sydney",
    "Melbourne",
    "Adelaide",
    "Brisbane",
    "Darwin",
    "Perth",
    "Hobart",
]

__all__ = [
    "CityLiteral",
    "CurrentWeather",
    "ForecastDay",
    "Forecast",
]
