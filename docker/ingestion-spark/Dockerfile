FROM ghcr.io/jaymztheking/sports-data-platform/spark:latest

USER root

# lxml (pulled in by pybaseball) must be compiled from source on ARM64.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    "pyspark>=3.5" \
    "pybaseball>=2.2" \
    "pydantic-settings>=2.0" \
    "pandas>=2.0" \
    "boto3"

WORKDIR /app
COPY src/ ./src/

# src/ lives at /app/src/ — add /app to PYTHONPATH so `from src.x import y` resolves.
ENV PYTHONPATH=/app

USER 185
