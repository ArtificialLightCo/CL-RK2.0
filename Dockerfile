# Dockerfile — CLÆRK 2.0 (FastAPI+Python+Bots)

FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2, WeasyPrint, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Add app files
COPY . .

# Non-root user (recommended)
RUN useradd -m claerkuser
USER claerkuser

EXPOSE 8000

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# Entrypoint for FastAPI backend (override for bots/workers)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
