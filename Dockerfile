FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libmediainfo0v5 \
    libmediainfo-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app

VOLUME ["/media"]

CMD ["python", "-m", "src.cli", "/media"]