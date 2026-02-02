FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      libgl1 \
      libglib2.0-0 \
      curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

# Copy manifests first (cache-friendly)
COPY pyproject.toml ./
# If you have one, also copy your lockfile:
# COPY uv.lock ./
# COPY poetry.lock ./

# Copy source BEFORE install so packaging finds it reliably
COPY src ./src

# Install your package (and its deps from pyproject)
RUN pip install --upgrade pip \
    && pip install .

# Ensure runtime dirs writable (OCR cache if enabled)
RUN mkdir -p /app/cache/ocr /tmp \
    && chown -R appuser:appuser /app /tmp

EXPOSE 8000
USER appuser

# More production-friendly: multiple workers
CMD ["python", "-m", "uvicorn", "ocr_service.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
