FROM apache/airflow:2.9.3-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

# PySpark (and the DAG tasks that act as Spark driver) need JAVA_HOME set.
ENV JAVA_HOME=/usr/lib/jvm/default-java

USER airflow

RUN pip install --no-cache-dir \
    "pyspark>=3.5" \
    "pybaseball>=2.2" \
    "pyiceberg>=0.7" \
    "nfl-data-py>=0.3" \
    "nba-api>=1.4" \
    "pydantic-settings>=2.0"
