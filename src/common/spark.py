from pyspark.sql import SparkSession

from src.common.config import settings


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
