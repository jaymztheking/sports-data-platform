import pandas as pd
from pyspark.sql import SparkSession

from src.common.config import settings


def sanitize_for_spark(pdf: pd.DataFrame) -> pd.DataFrame:
    """Cast columns containing dicts/lists to str so Spark can infer a flat schema.

    pybaseball occasionally returns object-dtype columns with mixed scalar/nested
    values. Spark's schema inference fails with CANNOT_MERGE_TYPE when it sees
    LongType in one row and StructType (dict) in another. Stringifying only the
    non-scalar values resolves the conflict while preserving None → null mapping.
    """
    for col in pdf.select_dtypes(include="object").columns:
        if pdf[col].apply(lambda x: isinstance(x, (dict, list))).any():
            pdf[col] = pdf[col].apply(
                lambda x: str(x) if isinstance(x, (dict, list)) else x
            )
    return pdf


def get_spark_session(app_name: str) -> SparkSession:
    """Create an Iceberg-configured SparkSession pointing to REST catalog + MinIO."""
    spark_cfg = settings.spark
    minio_cfg = settings.minio

    return (
        SparkSession.builder.appName(app_name)
        .master(spark_cfg.master_url)
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.iceberg.type", "rest")
        .config("spark.sql.catalog.iceberg.uri", spark_cfg.iceberg_catalog_uri)
        .config("spark.sql.catalog.iceberg.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
        .config("spark.sql.catalog.iceberg.s3.endpoint", spark_cfg.s3_endpoint)
        .config("spark.sql.catalog.iceberg.s3.path-style-access", "true")
        .config("spark.sql.defaultCatalog", "iceberg")
        .config("spark.hadoop.fs.s3a.endpoint", spark_cfg.s3_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", minio_cfg.access_key)
        .config("spark.hadoop.fs.s3a.secret.key", minio_cfg.secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )
