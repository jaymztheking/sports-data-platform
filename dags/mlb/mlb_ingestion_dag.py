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
        from src.domains.mlb.ingestion.schedules import ingest_schedules as _ingest

        mlb_teams = [
            "NYY", "BOS", "TBR", "TOR", "BAL",
            "CLE", "MIN", "CHW", "DET", "KCR",
            "HOU", "SEA", "TEX", "LAA", "OAK",
            "ATL", "NYM", "PHI", "MIA", "WSN",
            "MIL", "CHC", "STL", "PIT", "CIN",
            "LAD", "SDP", "SFG", "ARI", "COL",
        ]
        spark = get_spark_session("mlb_schedules_ingestion")
        try:
            _ingest(spark, season, mlb_teams)
        finally:
            spark.stop()

    @task
    def load_to_postgres() -> None:
        from src.common.postgres import get_engine
        from src.common.spark import get_spark_session
        from src.domains.mlb.loaders.iceberg_to_postgres import load_all_to_postgres

        spark = get_spark_session("mlb_iceberg_to_postgres")
        engine = get_engine()
        try:
            load_all_to_postgres(spark, engine)
        finally:
            spark.stop()
            engine.dispose()

    current_season = 2024

    statcast = ingest_statcast(start_dt="2024-03-28", end_dt="2024-09-29")
    batting = ingest_batting(season=current_season)
    pitching = ingest_pitching(season=current_season)
    schedules = ingest_schedules(season=current_season)

    load = load_to_postgres()
    [statcast, batting, pitching, schedules] >> load


mlb_ingestion()
