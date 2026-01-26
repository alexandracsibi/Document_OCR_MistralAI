FROM python:3.11-slim AS runtime

# Prevents Python from writing pyc files and enables unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps:
# - ca-certificates: HTTPS
# - libgl1 + libglib2.0-0: OpenCV runtime deps (safe default)
# - curl: useful for healthchecks/debugging
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      libgl1 \
      libglib2.0-0 \
      curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app

# Copy dependency manifests first for caching
COPY pyproject.toml ./
# COPY uv.lock ./

# Install dependencies:
RUN pip install --upgrade pip \
    && pip install .

# Copy source code
COPY src ./src

# Expose FastAPI port
EXPOSE 8000

# Run as non-root
USER appuser

# Assumes: src/ocr_service/api/main.py defines `app = FastAPI()`
CMD ["python", "-m", "uvicorn", "ocr_service.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
