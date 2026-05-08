# Multi-stage Dockerfile for ZipIt MLOps Platform
# Stage 1: Build dependencies and compile
FROM python:3.9-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=2.0.0
ARG VCS_REF

# Labels for metadata
LABEL maintainer="ZipIt MLOps Team" \
      version="${VERSION}" \
      description="Enterprise MLOps Platform" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r mlops && useradd -r -g mlops mlops

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production runtime
FROM python:3.9-slim as production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r mlops && useradd -r -g mlops mlops

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=mlops:mlops . .

# Create necessary directories
RUN mkdir -p models static templates logs && \
    chown -R mlops:mlops /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WORKERS=4 \
    LOG_LEVEL=info

# Security: Run as non-root user
USER mlops

# Expose port
EXPOSE 8000

# Health check with advanced monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Advanced startup with Gunicorn for production
CMD ["sh", "-c", "python -m uvicorn mlops_platform:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS} --log-level ${LOG_LEVEL} --access-log --loop uvloop --http httptools"]

# Stage 3: Development environment
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy \
    bandit \
    safety \
    pre-commit

# Switch back to mlops user
USER mlops

# Development command with hot reload
CMD ["python", "-m", "uvicorn", "mlops_platform:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]