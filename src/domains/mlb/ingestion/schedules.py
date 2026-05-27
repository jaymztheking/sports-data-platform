"""Ingest MLB game schedules into Iceberg via PySpark."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pybaseball
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.common.spark import pandas_schema_to_spark, sanitize_for_spark

# All 30 MLB franchises using pybaseball's schedule_and_record abbreviations
MLB_TEAMS: list[str] = [
    "ARI", "ATL", "BAL", "BOS", "CHC", "CHW", "CIN", "CLE", "COL", "DET",
    "HOU", "KCR", "LAA", "LAD", "MIA", "MIL", "MIN", "NYM", "NYY", "OAK",
    "PHI", "PIT", "SDP", "SEA", "SFG", "STL", "TBR", "TEX", "TOR", "WSN",
]


def fetch_schedule(season: int, team: str) -> pd.DataFrame:
    """Fetch schedule and record for a team/season using pybaseball."""
    return pybaseball.schedule_and_record(season, team)


def ingest_schedules(
    spark: SparkSession,
    season: int,
    teams: list[str] = MLB_TEAMS,
    table: str = "iceberg.mlb.schedules",
) -> None:
    """Fetch schedules for all teams and write to Iceberg table on MinIO."""
    all_schedules = []
    for team in teams:
        pdf = fetch_schedule(season, team)
        if not pdf.empty:
            pdf["team"] = team
            all_schedules.append(pdf)

    if not all_schedules:
        return

    combined = pd.concat(all_schedules, ignore_index=True)
    clean = sanitize_for_spark(combined)
    df = spark.createDataFrame(clean, schema=pandas_schema_to_spark(clean))
    df = df.withColumn("ingested_at", F.lit(datetime.utcnow().isoformat()))
    df = df.withColumn("source", F.lit("pybaseball.schedule_and_record"))
    df = df.withColumn("season", F.lit(season))

    df.writeTo(table).using("iceberg").partitionedBy("season").createOrReplace()
