# Not going into real prod, just grab latest. Would pin to LTS for real deployment.
FROM ubuntu:latest AS dev

ARG UV_VERSION=0.6.2

ENV DEBIAN_FRONTEND=noninteractive
ENV SHELL=/bin/bash

RUN apt-get update && apt-get install -y \
    bash-completion \
    build-essential \
    pipx \
    python3.12 \
    python3.12-dev \
    unzip \
    curl \
    git \
    libgl1 \
    micro \
    nodejs \
    npm
# && apt-get clean && rm -rf /var/lib/apt/lists/* # Would do this in real runtime images to keep things smaller.

# Python tooling.
RUN pipx ensurepath && pipx install "uv==$UV_VERSION"

# Node tooling.
RUN npm i -g corepack && corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm setup
RUN mkdir -p /usr/local/pnpm-bin
ENV PATH="/usr/local/pnpm-bin:${PATH}"
RUN pnpm config set global-bin-dir /usr/local/pnpm-bin
RUN pnpm add -g vite \
    && pnpm add -g @shadcn/ui \
    && pnpm add -g eslint \
    && pnpm add -g prettier

FROM dev AS build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app

ADD api .

RUN uv sync --no-install-project --no-dev

RUN uv sync --no-dev

FROM ubuntu:latest AS runtime

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