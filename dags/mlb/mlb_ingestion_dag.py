"""MLB Bronze Layer Ingestion DAG.

Fetches MLB data from pybaseball APIs and writes to Iceberg tables on MinIO.
"""

from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="mlb_ingestion",
    schedule="@weekly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["mlb", "ingestion", "bronze"],
)
def mlb_ingestion():
    @task
    def ingest_statcast(start_dt: str, end_dt: str) -> None:
        from src.common.spark import get_spark_session
        from src.domains.mlb.ingestion.statcast import ingest_statcast as _ingest

        spark = get_spark_session("mlb_statcast_ingestion")
        try:
            _ingest(spark, start_dt, end_dt)
        finally:
            spark.stop()

    @task
    def ingest_batting(season: int) -> None:
        from src.common.spark import get_spark_session
        from src.domains.mlb.ingestion.batting import ingest_batting as _ingest

        spark = get_spark_session("mlb_batting_ingestion")
        try:
            _ingest(spark, season)
        finally:
            spark.stop()

    @task
    def ingest_pitching(season: int) -> None:
        from src.common.spark import get_spark_session
        from src.domains.mlb.ingestion.pitching import ingest_pitching as _ingest

        spark = get_spark_session("mlb_pitching_ingestion")
        try:
            _ingest(spark, season)
        finally:
            spark.stop()

    @task
    def ingest_schedules(season: int) -> None:
        from src.common.spark import get_spark_session
        from src.domains.mlb.ingestion.schedules import MLB_TEAMS
        from src.domains.mlb.ingestion.schedules import ingest_schedules as _ingest

        spark = get_spark_session("mlb_schedules_ingestion")
        try:
            _ingest(spark, season, MLB_TEAMS)
        finally:
            spark.stop()

    current_season = 2024

    # Four independent ingestion tasks — no inter-dependencies, run in parallel.
    ingest_statcast(start_dt="2024-03-28", end_dt="2024-09-29")
    ingest_batting(season=current_season)
    ingest_pitching(season=current_season)
    ingest_schedules(season=current_season)


mlb_ingestion()
