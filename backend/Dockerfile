# Multi-stage production-ready Dockerfile for ReVivo Backend
FROM python:3.11-slim as base

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies (curl for healthchecks, netcat for db wait)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies in isolated layer for optimal caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create non-privileged user and setup directories
RUN addgroup --system --gid 10001 revivogroup && \
    adduser --system --uid 10001 --ingroup revivogroup --home /app revivouser

# Copy application source code and configuration
COPY . /app

# Make entrypoint script executable and set ownership
RUN chmod +x /app/entrypoint.sh && \
    chown -R revivouser:revivogroup /app

# Switch to non-root user
USER revivouser

EXPOSE 8000

# Healthcheck to verify container status
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]

# Default command runs Uvicorn ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
