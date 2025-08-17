from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus

from ..config import CITY_PRODUCT_IDS, FTP_FWO_PATH, FTP_HOST
from ..util.ftp import FtpClient


@dataclass
class BomClient:
    host: str = FTP_HOST
    directory: str = FTP_FWO_PATH

    def __post_init__(self) -> None:
        self.ftp = FtpClient(self.host)

    def _choose_city_file(self, city: str) -> str | None:
        product = CITY_PRODUCT_IDS.get(city)
        if product:
            # If product includes a slash, treat as full path under FTP root
            if product.endswith(".xml"):
                return f"{self.directory}/{product}" if not product.startswith("/") else product
            else:
                return f"{self.directory}/{product}.xml"
        # No exact mapping configured: enforce explicit configuration to avoid scans
        return None

    # Returns XML text for a given city
    def fetch_city_xml(self, city: str) -> tuple[int, str]:
        path = self._choose_city_file(city)
        if not path:
            raise ValueError(
                f"City '{city}' is not mapped to a product ID. Set CITY_PRODUCT_IDS in config.py."
            )
        return int(HTTPStatus.OK), self.ftp.fetch_text(path)

    def fetch_warnings_xml(self) -> tuple[int, str]:
        files = self.ftp.list_files(self.directory)
        warn_files = [f for f in files if f.endswith(".xml") and "warn" in f.lower()]
        warn_files.sort(reverse=True)
        if not warn_files:
            # Fallback: just return an empty structure
            return int(HTTPStatus.OK), "<warnings><none>No warnings</none></warnings>"
        path = f"{self.directory}/{warn_files[0]}"
        return int(HTTPStatus.OK), self.ftp.fetch_text(path)
