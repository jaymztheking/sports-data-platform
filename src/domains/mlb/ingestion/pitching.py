"""Ingest MLB season pitching statistics into Iceberg via PySpark."""

from datetime import datetime

import pandas as pd
import pybaseball
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.common.spark import pandas_schema_to_spark, sanitize_for_spark


def fetch_pitching_stats(season: int) -> pd.DataFrame:
    """Fetch season pitching stats from Baseball Reference via pybaseball."""
    return pybaseball.pitching_stats_bref(season)


def ingest_pitching(
    spark: SparkSession, season: int, table: str = "iceberg.mlb.pitching"
) -> None:
    """Fetch pitching stats and write to Iceberg table on MinIO."""
    pdf = fetch_pitching_stats(season)
    if pdf.empty:
        return

    clean = sanitize_for_spark(pdf)
    df = spark.createDataFrame(clean, schema=pandas_schema_to_spark(clean))
    df = df.withColumn("ingested_at", F.lit(datetime.utcnow().isoformat()))
    df = df.withColumn("source", F.lit("pybaseball.pitching_stats_bref"))
    df = df.withColumn("season", F.lit(season))

    df.writeTo(table).using("iceberg").partitionedBy("season").createOrReplace()
