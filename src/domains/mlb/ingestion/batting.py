"""Ingest MLB season batting statistics into Iceberg via PySpark."""

from datetime import datetime

import pandas as pd
import pybaseball
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def fetch_batting_stats(season: int) -> pd.DataFrame:
    """Fetch season batting stats using pybaseball."""
    return pybaseball.batting_stats(season)


def ingest_batting(spark: SparkSession, season: int) -> None:
    """Fetch batting stats and write to Iceberg table on MinIO."""
    pdf = fetch_batting_stats(season)
    if pdf.empty:
        return

    df = spark.createDataFrame(pdf)
    df = df.withColumn("ingested_at", F.lit(datetime.utcnow().isoformat()))
    df = df.withColumn("source", F.lit("pybaseball.batting_stats"))
    df = df.withColumn("season", F.lit(season))

    df.writeTo("iceberg.mlb.batting").using("iceberg").partitionedBy(
        "season"
    ).createOrReplace()
