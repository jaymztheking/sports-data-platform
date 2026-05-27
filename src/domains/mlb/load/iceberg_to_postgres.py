"""Load MLB Iceberg bronze tables into PostgreSQL raw_mlb schema."""

from pyspark.sql import SparkSession
from sqlalchemy import create_engine, text

from src.common.config import settings

TABLES = ["statcast", "batting", "pitching", "schedules"]


def load_table_to_postgres(
    spark: SparkSession,
    iceberg_table: str,
    pg_schema: str,
    pg_table: str,
) -> None:
    """Read one Iceberg table and write it to Postgres (replace semantics)."""
    engine = create_engine(settings.postgres.url)
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{pg_schema}"'))
    pdf = spark.table(iceberg_table).toPandas()
    pdf.to_sql(pg_table, engine, schema=pg_schema, if_exists="replace", index=False)


def load_all_to_postgres(
    spark: SparkSession,
    iceberg_ns: str = "iceberg.mlb",
    pg_schema: str = "raw_mlb",
) -> None:
    """Load all four MLB tables from Iceberg into Postgres."""
    for table in TABLES:
        load_table_to_postgres(
            spark,
            iceberg_table=f"{iceberg_ns}.{table}",
            pg_schema=pg_schema,
            pg_table=table,
        )
