Here’s an updated PROMPT.md with the directory structure baked in.

# PROMPT.md

You are building a new MCP (Model Context Protocol) server.

## Goals
- Expose tools which allow an LLM to request **weather data** from the Australian **Bureau of Meteorology (BoM)**.
- The MCP should convert the requests to FTP requests to the BOM FTP Server
  - BOM FTP Server is `ftp://ftp.bom.gov.au` and the default path is `/anon/gen`
  - The path `/anon/gen/fwo` contains all the weather data in `.xml` files.
  - The files that contain the city data are at the following files:
    - Sydney: `IDN60920.xml`
    - Melbourne: `IDV60920.xml`
    - Brisbane: `IDQ60920.xml`
    - Adelaide: `IDS60920.xml`
    - Hobart: `IDT60920.xml`
    - Perth: `IDW60920.xml`
    - Darwin: `IDD60920.xml`
- Supported cities: **Sydney, Melbourne, Adelaide, Brisbane, Darwin, Perth, Hobart**.
- Endpoints/tools:
  - **current_weather(city)**
  - **forecast(city)**
  - **current_weather_all_major_cities()** (aggregated)
  - **current_warnings** (aggregated)

## Tech / Standards
- **Modern Python** (>=3.13), dependency & venv via **`uv`**.
- **`ruff`** for lint + format (ruff format).
- Use an **early version of `ty`** for typing (type aliases, TypedDicts, etc.).
- Clean, typed, idiomatic Python. No unused deps.

## Directory Structure

mcp-bom-weather/
├─ pyproject.toml
├─ uv.lock
├─ README.md
├─ PROMPT.md
├─ .ruff.toml
├─ .gitignore
├─ src/
│  └─ mcp_bom_weather/
│     ├─ init.py
│     ├─ server.py                # MCP server bootstrap and tool registration
│     ├─ config.py                # Settings (API endpoints, timeouts, city mapping)
│     ├─ clients/
│     │  ├─ init.py
│     │  └─ bom_client.py         # BoM FTP client + response validators
│     ├─ tools/
│     │  ├─ init.py
│     │  ├─ schemas.py            # ty types/TypedDicts for requests/responses
│     │  └─ weather_tools.py      # Tool implementations (current, forecast, all)
│     ├─ adapters/
│     │  ├─ init.py
│     │  └─ bom_adapter.py        # Map BoM payloads → internal response models
│     └─ util/
│        ├─ init.py
│        └─ ftp.py               # Shared FTP session, retries, caching hooks
├─ tests/
│  ├─ conftest.py                 # pytest fixtures (fake clock, test client)
│  ├─ test_current_weather.py     # Parametrized over all cities
│  ├─ test_forecast.py            # Parametrized over all cities
│  └─ test_all_cities.py          # Aggregated tool behavior, ordering, errors
└─ scripts/
├─ dev-setup.sh                # uv sync, pre-commit, ruff, etc.
└─ run-server.sh               # Launch server locally

## Implementation Notes
- **BoM access**: use official FTP server available; keep a city→location-id map in `config.py`. Add simple response shape guards in `adapters/bom_adapter.py`.
- **Tools** (register in `server.py`):
  - `current_weather(city: str) -> CurrentWeather`
  - `forecast(city: str, days: int = 7) -> Forecast`
  - `current_weather_all_major_cities() -> list[CurrentWeather]`
- **Typing (`ty`)**:
  - Astral project for `ty`: https://github.com/astral-sh/ty
  - Define `CityLiteral = ty.Literal["Sydney","Melbourne","Adelaide","Brisbane","Darwin","Perth","Hobart"]`.
  - Response models as `TypedDict`/`ty.Struct` (e.g., `TempC`, `Condition`, `UpdatedAt`).
- **Errors**: predictable error codes/messages for unknown city, BoM downtime, and rate limits.

## Testing Requirements
- **Unit tests**: mock BoM FTP; deterministic fixtures.
- **Coverage**: all tools, all cities, error paths, schema validation.
- **Contract checks**: ensure tool schemas are stable (snapshot or JSONSchema round-trip).
- **Parametrization**: run each tool across the 7 cities.

## Example Scaffolding (snippets the generator should produce)
- `pyproject.toml`:
  - `[project]` with `src` layout.
  - deps: `ty`, `pytest`, `pytest-asyncio`, `ruff`.
  - optional: `anyio` for async, `cachetools` for simple memo.
- `.ruff.toml`: enable format; select `E,F,I,UP,PL,ANN` rules; target py311.
- `scripts/dev-setup.sh`: `uv sync && ruff check --fix && ruff format`.
- `scripts/run-server.sh`: runs `python -m mcp_bom_weather.server`.

## Non-Goals
- No UI. No non-BoM providers. Keep scope to the 7 cities + BoM.

## Deliverable
A working MCP server that:
- Registers the three tools and returns typed, validated responses.
- Fetches from BoM reliably with clear errors.
- Is formatted with `ruff`, typed with `ty`, and fully covered by tests.

If you want, I can also draft the pyproject.toml and minimal stubs for server.py, weather_tools.py, and the test files so you can uv sync and run immediately.
