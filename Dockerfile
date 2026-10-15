# Multi-stage Dockerfile for Ragas Contrastive Evaluation Studio
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications first for layer caching
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir fastapi uvicorn pydantic starlette pytest httpx

# Copy project source code
COPY src/ /app/src/
COPY ragas_dashboard/ /app/ragas_dashboard/
COPY tests/ /app/tests/
COPY run_dashboard.py /app/run_dashboard.py
COPY README.md /app/README.md

# Install local package in editable mode
RUN pip install --no-cache-dir -e .

# Expose server port
EXPOSE 8000

# Healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Launch the Ragas Evaluation Studio
CMD ["python", "run_dashboard.py", "--host", "0.0.0.0", "--port", "8000", "--no-browser"]
