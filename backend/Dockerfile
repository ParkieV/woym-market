FROM python:3.10.5-slim AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Moscow

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists \
    rm -f /var/lib/apt/lists/lock /var/cache/apt/archives/lock /var/lib/dpkg/lock-frontend && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates libstdc++6 libpq5 git && \
    rm -rf /var/lib/apt/lists/*

FROM base AS builder

ENV VENV_PATH=/opt/venv
ENV PATH="${VENV_PATH}/bin:${PATH}" \
    VIRTUAL_ENV="${VENV_PATH}"

RUN python -m venv "${VENV_PATH}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ libpq-dev python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install -r /tmp/requirements.txt

FROM base AS runtime

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv" \
    PYTHONPATH="/home/app:${PYTHONPATH}"

WORKDIR /src

COPY . app

EXPOSE 8000

CMD ["python3", "app/main.py"]