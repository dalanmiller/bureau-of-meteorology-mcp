# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy project metadata and source
COPY pyproject.toml README.md PROMPT.md /app/
COPY src /app/src

# Install dependencies into a local virtual environment using uv (no dev deps)
RUN uv sync --no-dev

# Ensure the venv is used for subsequent commands
ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 4242 8765

# Default to FastMCP HTTP (Streamable) transport. Override to stdio with:
#   docker run -it --rm bom-mcp python -m mcp_bom_weather.fast_mcp_server --stdio
CMD ["python", "-m", "mcp_bom_weather.fast_mcp_server", "--http", "--host", "0.0.0.0", "--port", "4242"]
