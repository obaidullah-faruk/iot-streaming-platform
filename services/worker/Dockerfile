FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the database package
COPY database/ ./database/

# Copy the app directory
COPY services/worker/app/ ./app/

ENV PYTHONPATH=/app

CMD ["python", "app/consumer.py"]
