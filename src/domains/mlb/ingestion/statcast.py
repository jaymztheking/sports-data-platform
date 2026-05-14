"""Ingest Statcast pitch-level tracking data into Iceberg via PySpark."""

from datetime import datetime

import pandas as pd
import pybaseball
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def fetch_statcast(start_dt: str, end_dt: str) -> pd.DataFrame:
    """Fetch Statcast data for a date range using pybaseball."""
    return pybaseball.statcast(start_dt=start_dt, end_dt=end_dt)


def ingest_statcast(spark: SparkSession, start_dt: str, end_dt: str) -> None:
    """Fetch Statcast data and write to Iceberg table on MinIO."""
    pdf = fetch_statcast(start_dt, end_dt)
    if pdf.empty:
        return

    df = spark.createDataFrame(pdf)
    df = df.withColumn("ingested_at", F.lit(datetime.utcnow().isoformat()))
    df = df.withColumn("source", F.lit("pybaseball.statcast"))
    df = df.withColumn("season", F.year(F.col("game_date")))

    df.writeTo("iceberg.mlb.statcast").using("iceberg").partitionedBy(
        "season"
    ).createOrReplace()
