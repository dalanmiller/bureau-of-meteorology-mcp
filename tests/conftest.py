from __future__ import annotations

from pathlib import Path

import pytest

from mcp_bom_weather.clients.bom_client import BomClient
from mcp_bom_weather.config import CITY_PRODUCT_IDS


class ExamplesClient(BomClient):
    def __init__(self, examples_dir: Path) -> None:  # type: ignore[no-untyped-def]
        self.examples_dir = examples_dir

    def fetch_city_xml(self, city: str) -> tuple[int, str]:  # type: ignore[override]
        product = CITY_PRODUCT_IDS[city]
        assert product, f"No product configured for {city} in CITY_PRODUCT_IDS"
        path = self.examples_dir / f"{product}.xml"
        text = path.read_text(encoding="utf-8")
        return 200, text

    def fetch_warnings_xml(self) -> tuple[int, str]:  # type: ignore[override]
        # Prefer a known warnings example if provided; otherwise fall back to minimal
        # If repository includes a CAP or warnings file in examples, point here.
        # For now, return a simple single warning so parser path is exercised.
        xml = """
        <warnings>
          <warning>Severe Weather Warning</warning>
        </warnings>
        """
        return 200, xml


@pytest.fixture(scope="session")
def examples_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "examples"


@pytest.fixture()
def examples_client(examples_dir: Path) -> ExamplesClient:
    return ExamplesClient(examples_dir)
