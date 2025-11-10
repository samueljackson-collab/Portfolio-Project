FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY config/ config/

# Create non-root user
RUN useradd -m -u 1000 migrator && \
    chown -R migrator:migrator /app
USER migrator

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Run the migration orchestrator
ENTRYPOINT ["python", "-m", "src.migration_orchestrator"]
