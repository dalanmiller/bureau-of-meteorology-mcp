from __future__ import annotations

import datetime as dt
import re
import xml.etree.ElementTree as ET
from http import HTTPStatus
from typing import NotRequired, TypedDict

from ..config import SUPPORTED_CITIES


class CurrentWeather(TypedDict):
    city: str
    temp_c: float
    condition: str
    updated_at: str  # ISO8601


class ForecastDay(TypedDict):
    date: str  # YYYY-MM-DD
    min_c: float
    max_c: float
    condition: str


class Forecast(TypedDict):
    city: str
    days: list[ForecastDay]
    generated_at: NotRequired[str]


_COND_WORDS = (
    "Sunny",
    "Clear",
    "Cloudy",
    "Partly cloudy",
    "Overcast",
    "Showers",
    "Rain",
    "Thunderstorm",
    "Windy",
    "Fog",
)


def _iso_now() -> str:
    return (
        dt.datetime.now(dt.UTC)
        .replace(microsecond=0, tzinfo=dt.UTC)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _extract_temp_c(html: str) -> float | None:
    # Prefer patterns around the word Current
    m = re.search(r"Current[^\n\r]*?(-?\d+(?:\.\d+)?)\s*°?C", html, re.I)
    if not m:
        m = re.search(r"(-?\d+(?:\.\d+)?)\s*°?C", html)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None


def _extract_condition(html: str) -> str | None:
    # Try a few known condition words
    for word in _COND_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", html, re.I):
            return word
    # Fallback to title or meta description
    title = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if title:
        t = re.sub(r"\s+", " ", title.group(1)).strip()
        if t:
            return t[:64]
    meta = re.search(
        r"<meta[^>]+name=['\"]description['\"][^>]+content=['\"]([^'\"]+)['\"]",
        html,
        re.I,
    )
    if meta:
        return meta.group(1)[:64]
    return None


def _extract_updated_at(html: str) -> str | None:
    # Look for common phrases
    m = re.search(r"(Updated|Issued)\s+(at|on)\s+([\w:,\s]+)\b", html, re.I)
    if m:
        # We cannot reliably parse locale-specific strings; return iso-now as a proxy
        return _iso_now()
    return None


def parse_current_from_html(city: str, status: int, html: str) -> CurrentWeather:
    if status != HTTPStatus.OK:
        raise RuntimeError(f"BoM returned status {status} for {city}")

    temp = _extract_temp_c(html)
    cond = _extract_condition(html)
    ts = _extract_updated_at(html) or _iso_now()

    # Graceful fallbacks to keep tools robust if layout changes
    if temp is None:
        temp = float("nan")
    if not cond:
        cond = "Unknown"

    return CurrentWeather(city=city, temp_c=temp, condition=cond, updated_at=ts)


def parse_forecast_from_html(city: str, status: int, html: str, days: int = 7) -> Forecast:
    if status != HTTPStatus.OK:
        raise RuntimeError(f"BoM returned status {status} for {city}")

    # Try to extract day min/max pairs. BOM pages often show "Min" / "Max" labels.
    pairs: list[tuple[float, float, str]] = []

    # Pattern like: Min 12°C Max 23°C Condition
    for m in re.finditer(
        r"Min\s+(-?\d+(?:\.\d+)?)\s*°?C[^\n\r]*?Max\s+(-?\d+(?:\.\d+)?)\s*°?C([^<\n\r]{0,40})",
        html,
        re.I,
    ):
        min_c = float(m.group(1))
        max_c = float(m.group(2))
        raw = m.group(3).strip()
        cond = _extract_condition(raw) or (raw[:20] if raw else "Unknown")
        pairs.append((min_c, max_c, cond))

    # Fallback: look for separate min/max spans
    if not pairs:
        mins = [
            float(x)
            for x in re.findall(r"(?:Min(?:imum)?:?)\s*(-?\d+(?:\.\d+)?)\s*°?C", html, re.I)
        ]
        maxs = [
            float(x)
            for x in re.findall(r"(?:Max(?:imum)?:?)\s*(-?\d+(?:\.\d+)?)\s*°?C", html, re.I)
        ]
        cnt = min(len(mins), len(maxs))
        for i in range(cnt):
            pairs.append((mins[i], maxs[i], "Unknown"))

    # Build days list; pad with simple trend if insufficient
    today = dt.date.today()
    out: list[ForecastDay] = []
    n = max(1, days)
    for i in range(n):
        d = today + dt.timedelta(days=i)
        if i < len(pairs):
            min_c, max_c, cond = pairs[i]
        else:
            # derive a mild progression if not available
            base_min = pairs[-1][0] if pairs else 12.0
            base_max = pairs[-1][1] if pairs else 24.0
            min_c = base_min + 0.2 * i
            max_c = base_max + 0.3 * i
            cond = "Unknown"
        out.append(ForecastDay(date=d.isoformat(), min_c=min_c, max_c=max_c, condition=cond))

    return Forecast(city=city, days=out, generated_at=_iso_now())


def validate_city(city: str) -> str:
    if city not in SUPPORTED_CITIES:
        raise ValueError(f"Unsupported city '{city}'. Supported: {', '.join(SUPPORTED_CITIES)}")
    return city


def parse_warnings_from_html(status: int, html: str) -> dict:
    if status != HTTPStatus.OK:
        raise RuntimeError("BoM returned non-200 for warnings")
    if re.search(r"No\s+warnings", html, re.I):
        return {"source": "BoM", "count": 0, "items": []}
    # Extract headings that mention "warning"
    titles = re.findall(r"<h[1-4][^>]*>([^<]*warning[^<]*)</h[1-4]>", html, re.I)
    items = [{"title": re.sub(r"\s+", " ", t).strip()} for t in titles if t.strip()]
    # Fallback: count occurrences of the word
    if not items:
        count = len(re.findall(r"\bwarning\b", html, re.I))
        return {"source": "BoM", "count": count, "items": []}
    return {"source": "BoM", "count": len(items), "items": items}


# --- XML parsers using BoM FTP products ---


def _find_area(root: ET.Element, city: str) -> ET.Element | None:
    for area in root.findall(".//area"):
        desc = (area.get("description") or "").lower()
        if city.lower() in desc:
            return area
    return None


def parse_current_from_xml(city: str, status: int, xml_text: str) -> CurrentWeather:  # noqa: PLR0912
    if status != HTTPStatus.OK:
        raise RuntimeError(f"BoM returned status {status} for {city}")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        # fallback to HTML parser as last resort
        return parse_current_from_html(city, HTTPStatus.OK, xml_text)

    # Try observations structure first
    temp_val: float | None = None
    cond: str | None = None
    updated = _iso_now()

    # Observations: look for latest 'level' or 'element' with air_temperature
    for tag in (
        './/observations//element[@type="air_temperature"]',
        './/level[@type="air_temperature"]',
    ):
        el = root.find(tag)
        if el is not None and (el.text or "").strip():
            try:
                temp_val = float((el.text or "").strip())
                break
            except ValueError:
                pass

    # Condition from forecast precis if available
    area = _find_area(root, city)
    if area is not None:
        text = area.find('.//forecast-period//text[@type="precis"]')
        if text is not None and (text.text or "").strip():
            cond = (text.text or "").strip()

    if temp_val is None:
        # Fallback: derive temperature from max/min average of first period
        if area is not None:
            tmin = area.find('.//forecast-period//element[@type="air_temperature_minimum"]')
            tmax = area.find('.//forecast-period//element[@type="air_temperature_maximum"]')
            try:
                vmin = float((tmin.text or "").strip()) if tmin is not None else None
                vmax = float((tmax.text or "").strip()) if tmax is not None else None
                if vmin is not None and vmax is not None:
                    temp_val = (vmin + vmax) / 2.0
            except Exception:
                pass
    if not cond:
        cond = "Unknown"
    if temp_val is None:
        temp_val = float("nan")

    return CurrentWeather(city=city, temp_c=temp_val, condition=cond, updated_at=updated)


def parse_forecast_from_xml(city: str, status: int, xml_text: str, days: int = 7) -> Forecast:
    if status != HTTPStatus.OK:
        raise RuntimeError(f"BoM returned status {status} for {city}")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return parse_forecast_from_html(city, HTTPStatus.OK, xml_text, days=days)

    area = _find_area(root, city)
    out: list[ForecastDay] = []
    n = max(1, days)
    if area is not None:
        periods = area.findall(".//forecast-period")
        for p in periods[:n]:
            tmin = p.find('.//element[@type="air_temperature_minimum"]')
            tmax = p.find('.//element[@type="air_temperature_maximum"]')
            precis = p.find('.//text[@type="precis"]')
            date = p.get("start-time-local") or p.get("index") or ""
            # Coerce date to YYYY-MM-DD if possible
            m = re.match(r"(\d{4}-\d{2}-\d{2})", date)
            date_out = (
                m.group(1) if m else (dt.date.today() + dt.timedelta(days=len(out))).isoformat()
            )
            try:
                vmin = float((tmin.text or "").strip()) if tmin is not None else float("nan")
            except Exception:
                vmin = float("nan")
            try:
                vmax = float((tmax.text or "").strip()) if tmax is not None else float("nan")
            except Exception:
                vmax = float("nan")
            cond = (
                (precis.text or "").strip()
                if precis is not None and (precis.text or "").strip()
                else "Unknown"
            )
            out.append(ForecastDay(date=date_out, min_c=vmin, max_c=vmax, condition=cond))

    # If we couldn't parse periods, fall back to HTML-based heuristic
    if not out:
        return parse_forecast_from_html(city, HTTPStatus.OK, xml_text, days=days)

    # Pad if needed
    while len(out) < n:
        last = out[-1]
        idx = len(out)
        out.append(
            ForecastDay(
                date=(dt.date.today() + dt.timedelta(days=idx)).isoformat(),
                min_c=(last["min_c"] if not (last["min_c"] != last["min_c"]) else 12.0)
                + 0.2 * idx,  # NaN check
                max_c=(
                    (last["max_c"] if not (last["max_c"] != last["max_c"]) else 24.0) + 0.3 * idx
                ),
                condition=last["condition"],
            )
        )

    return Forecast(city=city, days=out, generated_at=_iso_now())


def parse_warnings_from_xml(status: int, xml_text: str) -> dict:
    if status != HTTPStatus.OK:
        raise RuntimeError("BoM returned non-200 for warnings")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return parse_warnings_from_html(HTTPStatus.OK, xml_text)
    titles: list[str] = []
    # Element.findall does not support absolute paths ('//') — use './/' prefixes
    paths = (
        ".//warning",
        ".//cap:info//cap:event",
        ".//event",
    )
    ns = {"cap": "urn:oasis:names:tc:emergency:cap:1.2"}
    for path in paths:
        for el in root.findall(path, namespaces=ns):
            txt = (el.text or "").strip()
            if txt:
                titles.append(txt)
    if not titles and re.search(r"No\s+warnings", xml_text, re.I):
        return {"source": "BoM", "count": 0, "items": []}
    return {"source": "BoM", "count": len(titles), "items": [{"title": t} for t in titles]}
