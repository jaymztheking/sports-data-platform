FROM ghcr.io/jaymztheking/sports-data-platform/spark:latest

USER root

RUN pip3 install --no-cache-dir \
    "pybaseball>=2.2" \
    "pydantic-settings>=2.0" \
    "pandas>=2.0" \
    "boto3"

WORKDIR /app
COPY src/ ./src/

# src/ lives at /app/src/ — add /app to PYTHONPATH so `from src.x import y` resolves.
ENV PYTHONPATH=/app

USER 185
