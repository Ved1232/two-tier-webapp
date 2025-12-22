FROM python:3.12-slim

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

# Gunicorn for production-like runs (even locally in containers)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "src.app:app"]
