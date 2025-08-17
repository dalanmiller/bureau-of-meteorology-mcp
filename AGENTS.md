# Repository Guidelines

## Project Structure & Module Organization
- Keep source in `src/`, tests in `tests/`, scripts in `scripts/`, assets in `assets/`, and docs in `docs/`.
- Mirror modules in `tests/` to match `src/` paths for clarity.
- Example:
  - `src/`
  - `tests/`
  - `scripts/`
  - `docs/`
  - `assets/`

## Build, Test, and Development Commands
- Install deps: `uv sync` (or `pip install -e .[dev]`).
- Lint: `ruff check`; format: `ruff format`.
- Tests: `pytest -q` (offline; FTP is mocked with `examples/`).
- FastMCP stdio: `scripts/run-fastmcp.sh --stdio` (default if no flag provided).
- FastMCP HTTP (Streamable): `scripts/run-fastmcp.sh --http --host 0.0.0.0 --port 4242`.
- Note: `--stdio` and `--http` are mutually exclusive flags.

## Coding Style & Naming Conventions
- Indentation: 2 spaces for JS/TS; 4 spaces for Python. Max line length: 100.
- Naming: `snake_case` for Python modules; `camelCase` for variables/functions; `PascalCase` for classes; `kebab-case` for folders and packages.
- Formatting/Linting: add and run `prettier`/`eslint` (JS/TS) or `black`/`ruff` (Python) before opening a PR.

## Testing Guidelines
- Place tests under `tests/` mirroring `src/` structure.
- Naming: `test_*.py` (Python) or `*.spec.ts`/`*.test.ts` (TS/JS).
- Coverage: aim for 80%+. Run via `make test` (or `pytest`/`npm test` once configured).
 - Real fixtures: tests read actual BoM XML samples from `examples/` (e.g., `IDN60920.xml`, `IDV60920.xml`). Keep fixtures updated when schemas change.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `ci`.
- Example: `feat(weather): add rainfall parser`.
- PRs: keep changes focused; include purpose, linked issues, test plan, and screenshots if UI. Ensure CI, tests, and linters pass.

## Security & Configuration
- Never commit secrets. Use `.env` locally and commit a redacted `.env.example`.
- Pin toolchains with `.tool-versions`, `.nvmrc`, or `.python-version`.
 - Offline tests: the FTP client is mocked; fixtures in `examples/` ensure determinism.

## Architecture Notes
- Official MCP Python SDK FastMCP for stdio and streamable HTTP transport.
- FTP-first: XML from `ftp://ftp.bom.gov.au/anon/gen/fwo/`.
- Product IDs per city in `src/mcp_bom_weather/config.py` (e.g., Sydney `IDN60920`). No FTP scans.
- Layers: Clients (FTP) → Adapters (XML → models) → Tools (public API) → MCP bindings (SDK/FastMCP).

## Docker
- Build: `docker build -t bom-mcp .`
- Run FastMCP HTTP: `docker run -p 4242:4242 bom-mcp`
 

## Open WebUI
- Add MCP server: Settings → Tools → MCP Servers → Add.
- Command: `uv run -q python -m mcp_bom_weather.fast_mcp_server --stdio`.
- Note: Open WebUI expects stdio; HTTP/SSE endpoints are for other MCP hosts that support streamable HTTP.
