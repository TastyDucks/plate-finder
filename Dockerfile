# Not going into real prod, just grab latest. Would pin to LTS for real deployment.
FROM ubuntu:latest as dev

ARG UV_VERSION=0.6.2

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    pipx \
    python3.12 \
    python3.12-dev \
    unzip \
    curl \
    git \
    micro
# && apt-get clean && rm -rf /var/lib/apt/lists/* # Would do this in real runtime images to keep things smaller.

RUN pipx ensurepath && pipx install "uv==$UV_VERSION"

# Grab the dataset and dump images into the plates directory. This dataset actually includes bounding boxes but I'll delete them in the spirit of the task.
#RUN mkdir plates && cd plates && curl -L "https://universe.roboflow.com/ds/ScF3W2xwYJ?key=U0grCHK5DR" -o plates.zip \
#    && unzip plates.zip && rm plates.zip \
#    && mv test/images/*.jpg . && rm -rf test \
#    && mv train/images/*.jpg . && rm -rf train \
#    && mv valid/images/*.jpg . && rm -rf valid

# On second thought I'm going to store them with git LFS and ship them in the container.

FROM dev AS build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

WORKDIR /app

ADD . .

RUN uv sync --frozen --no-install-project --no-dev

RUN uv sync --frozen --no-dev

FROM dev AS runtime

COPY --from=build /app /app
#RUN mv /plates /app/src/plates
ENV PATH="/app/.venv/bin:${PATH}"
WORKDIR /app/src
EXPOSE 80
CMD ["python3.12", "main.py"]