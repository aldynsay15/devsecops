FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        libssl-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim-bookworm AS final

LABEL maintainer="security@example.com" \
      org.opencontainers.image.title="fastapi-secure-demo" \
      org.opencontainers.image.description="Demo FastAPI app with intentional vulnerabilities for DevSecOps CI/CD showcase" \
      org.opencontainers.image.vendor="DevSecOps Demo" \
      security.scanning.date="${BUILD_DATE}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random

# Создаем непривилегированного пользователя!
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --gid 1001 --no-create-home appuser

# Устанавливаем только необходимые runtime пакеты
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    truncate -s 0 /var/log/*log

COPY --from=builder --chown=appuser:appuser /venv /venv

ENV PATH="/venv/bin:$PATH"

WORKDIR /app

COPY --chown=appuser:appuser ./app /app/app
COPY --chown=appuser:appuser ./alembic.ini /app/
COPY --chown=appuser:appuser ./.env /app/.env

# Проверка целостности критичных файлов
RUN find /app -type f -name "*.py" -exec sha256sum {} \; > /app/checksums.txt && \
    chmod 400 /app/checksums.txt

# Запускаем от непривилегированного пользователя!
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
