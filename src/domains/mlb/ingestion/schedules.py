"""Ingest MLB game schedules into Iceberg via PySpark."""

from datetime import datetime

import pandas as pd
import pybaseball
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def fetch_schedule(season: int, team: str) -> pd.DataFrame:
    """Fetch schedule and record for a team/season using pybaseball."""
    return pybaseball.schedule_and_record(season, team)


def ingest_schedules(spark: SparkSession, season: int, teams: list[str]) -> None:
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
    df = spark.createDataFrame(combined)
    df = df.withColumn("ingested_at", F.lit(datetime.utcnow().isoformat()))
    df = df.withColumn("source", F.lit("pybaseball.schedule_and_record"))
    df = df.withColumn("season", F.lit(season))

    df.writeTo("iceberg.mlb.schedules").using("iceberg").partitionedBy(
        "season"
    ).createOrReplace()
