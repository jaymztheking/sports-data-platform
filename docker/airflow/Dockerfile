FROM apache/airflow:2.9.3-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
USER airflow

RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.3/constraints-3.11.txt" \
    "pyspark>=3.5" \
    "pybaseball>=2.2" \
    "pyiceberg>=0.7" \
    "nfl-data-py>=0.3" \
    "nba-api>=1.4"
