from __future__ import annotations

from typing import Final

# Supported cities as per prompt
SUPPORTED_CITIES: Final[list[str]] = [
    "Sydney",
    "Melbourne",
    "Adelaide",
    "Brisbane",
    "Darwin",
    "Perth",
    "Hobart",
]

# FTP settings
FTP_HOST: Final[str] = "ftp.bom.gov.au"
FTP_BASE_PATH: Final[str] = "/anon/gen"
FTP_FWO_PATH: Final[str] = "/anon/gen/fwo"

# City → state/product prefix mapping (BoM product IDs commonly begin with these prefixes)
# NSW: IDN, VIC: IDV, SA: IDS, QLD: IDQ, NT: IDD, WA: IDW, TAS: IDT
CITY_PRODUCT_PREFIX: Final[dict[str, str]] = {
    "Sydney": "IDN",
    "Melbourne": "IDV",
    "Adelaide": "IDS",
    "Brisbane": "IDQ",
    "Darwin": "IDD",
    "Perth": "IDW",
    "Hobart": "IDT",
}

# Exact product IDs per city (without .xml). If set, the client will fetch
# this file directly instead of scanning the directory. Leave as None to
# indicate it must be configured per environment.
CITY_PRODUCT_IDS: Final[dict[str, str | None]] = {
    # Per PROMPT.md, these map directly to files in /anon/gen/fwo
    # Store without .xml; client appends it
    "Sydney": "IDN60920",
    "Melbourne": "IDV60920",
    "Adelaide": "IDS60920",
    "Brisbane": "IDQ60920",
    "Darwin": "IDD60920",
    "Perth": "IDW60920",
    "Hobart": "IDT60920",
}

# Retry settings
FTP_TIMEOUT_SECS: Final[float] = 15.0
MAX_RETRIES: Final[int] = 3
