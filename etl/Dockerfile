# ETL Pipeline Dockerfile (Optimized)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install PyTorch CPU-only first (smaller, faster)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Then install other dependencies (this will skip torch if already installed)
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL code
COPY . .

# Set Python path to include workspace (for imports from backend, etc.)
ENV PYTHONPATH=/workspace:/app

# Default command (can be overridden in docker-compose)
CMD ["python", "main.py"]