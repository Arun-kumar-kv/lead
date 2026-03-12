# ============================================================
# Leads Analytics Dashboard - Dockerfile (PostgreSQL)
# ============================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# libpq-dev is required for psycopg2 (PostgreSQL client)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8200
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8200/health || exit 1

# Default command - run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8200", "--reload"]
