FROM ubuntu:latest AS build

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app

ADD . .

RUN uv sync --no-install-project --no-dev

RUN uv sync --no-dev

FROM ubuntu:latest AS runtime

LABEL org.opencontainers.image.description="Plate-finder API container."
LABEL org.opencontainers.image.source="https://github.com/tastyducks/plate-finder"

RUN apt-get update && apt-get install -y \
    python3.12 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=build /app /app
ENV PATH="/app/.venv/bin:${PATH}"
WORKDIR /app/src
EXPOSE 8000
CMD ["python3.12", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]