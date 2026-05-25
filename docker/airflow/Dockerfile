FROM apache/airflow:2.9.3-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
USER airflow

# Only packages needed by DAG definitions themselves (not by compute tasks).
# Compute runs in ingestion-spark pods via KubernetesPodOperator.
RUN pip install --no-cache-dir \
    "pydantic-settings>=2.0"
