"""Ingest MLB season pitching statistics into Iceberg via PySpark."""

from datetime import datetime

import pandas as pd
import pybaseball
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def fetch_pitching_stats(season: int) -> pd.DataFrame:
    """Fetch season pitching stats using pybaseball."""
    return pybaseball.pitching_stats(season)


def ingest_pitching(spark: SparkSession, season: int) -> None:
    """Fetch pitching stats and write to Iceberg table on MinIO."""
    pdf = fetch_pitching_stats(season)
    if pdf.empty:
        return

    df = spark.createDataFrame(pdf)
    df = df.withColumn("ingested_at", F.lit(datetime.utcnow().isoformat()))
    df = df.withColumn("source", F.lit("pybaseball.pitching_stats"))
    df = df.withColumn("season", F.lit(season))

    df.writeTo("iceberg.mlb.pitching").using("iceberg").partitionedBy(
        "season"
    ).createOrReplace()
