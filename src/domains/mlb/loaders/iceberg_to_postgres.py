"""Load Iceberg tables from MinIO into PostgreSQL raw_mlb schema."""

from pyspark.sql import SparkSession
from sqlalchemy import Engine

ICEBERG_TABLES = ["mlb.statcast", "mlb.batting", "mlb.pitching", "mlb.schedules"]


def load_table_to_postgres(spark: SparkSession, engine: Engine, table_name: str) -> None:
    """Read an Iceberg table and write it to the raw_mlb Postgres schema."""
    df = spark.read.format("iceberg").load(f"iceberg.{table_name}")
    pdf = df.toPandas()

    short_name = table_name.split(".")[-1]

    pdf.to_sql(
        name=short_name,
        con=engine,
        schema="raw_mlb",
        if_exists="replace",
        index=False,
    )


def load_all_to_postgres(spark: SparkSession, engine: Engine) -> None:
    """Load all MLB Iceberg tables into PostgreSQL."""
    for table in ICEBERG_TABLES:
        load_table_to_postgres(spark, engine, table)
