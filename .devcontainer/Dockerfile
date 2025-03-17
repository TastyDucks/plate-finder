# Not going into real prod, just grab latest. Would pin to LTS for real deployment.
FROM ubuntu:latest AS dev

LABEL org.opencontainers.image.description="Plate-finder dev container."
LABEL org.opencontainers.image.source="https://github.com/tastyducks/plate-finder"

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

    # GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg -o /usr/share/keyrings/githubcli.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list && \
    # Docker CLI
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list

RUN apt-get update && apt-get install -y \
    docker-buildx-plugin \
    docker-ce-cli \
    gh

RUN --mount=type=cache,target=/root/.cache/act \
    curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/nektos/act/master/install.sh | bash