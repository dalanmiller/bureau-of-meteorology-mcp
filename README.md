# mcp-bom-weather

Tools for an MCP (Model Context Protocol) server that exposes Australian Bureau of Meteorology (BoM) weather data for seven major cities via the BoM FTP XML feed.

Quick start
- Ensure Python >= 3.13 and `uv` are installed.
- Install: `uv sync` (or `pip install -e .[dev]`).
- Lint/format: `ruff check --fix && ruff format`.
- Run tests: `pytest -q`.
- Run FastMCP (stdio): `scripts/run-fastmcp.sh --stdio`.
- Run FastMCP HTTP (Streamable): `scripts/run-fastmcp.sh --http --host 0.0.0.0 --port 4242`.

CLI flags (FastMCP)
- `--stdio`: run with stdio transport (default if no flag is provided).
- `--http`: run Streamable HTTP/SSE transport; combine with `--host` and `--port` to configure bind address.

FTP configuration
- The client fetches XML from `ftp://ftp.bom.gov.au/anon/gen/fwo/` using exact product IDs per city in `mcp_bom_weather/config.py`:
  - Sydney: `IDN60920`, Melbourne: `IDV60920`, Brisbane: `IDQ60920`, Adelaide: `IDS60920`, Darwin: `IDD60920`, Perth: `IDW60920`, Hobart: `IDT60920`.
  - Files are `{PRODUCT}.xml` under `/anon/gen/fwo`.

Open WebUI integration (MCP)
- In Open WebUI, go to Settings → Tools → MCP Servers → Add.
- Name: `bom-weather`
- Command: `uv run -q python -m mcp_bom_weather.fast_mcp_server --stdio`
- Working Dir: repository root
- Save and test. Open WebUI will spawn the server via stdio and list the tools.

FastMCP HTTP (Streamable) transport
- Start: `scripts/run-fastmcp.sh --http --host 0.0.0.0 --port 4242`
- Docker: `docker build -t bom-mcp . && docker run -p 4242:4242 bom-mcp`
- Note: Open WebUI currently uses stdio. Other MCP hosts that support HTTP/SSE can connect to the FastMCP endpoint.

See PROMPT.md for the full design brief.
