import numpy as np
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    BooleanType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from src.common.config import settings

# Map pandas dtype strings to Spark types.  Anything not listed falls back to StringType.
_DTYPE_MAP = {
    "int8": IntegerType(),
    "int16": IntegerType(),
    "int32": IntegerType(),
    "int64": LongType(),
    "Int8": IntegerType(),
    "Int16": IntegerType(),
    "Int32": IntegerType(),
    "Int64": LongType(),
    "uint8": IntegerType(),
    "uint16": IntegerType(),
    "uint32": LongType(),
    "uint64": LongType(),
    "float32": FloatType(),
    "float64": DoubleType(),
    "Float32": FloatType(),
    "Float64": DoubleType(),
    "bool": BooleanType(),
    "boolean": BooleanType(),
    "datetime64[ns]": TimestampType(),
    "datetime64[us]": TimestampType(),
}


def _spark_type_for(dtype):  # type: ignore[type-arg]
    key = str(dtype)
    if key.startswith("datetime64"):
        return TimestampType()
    return _DTYPE_MAP.get(key, StringType())


def pandas_schema_to_spark(pdf: pd.DataFrame) -> StructType:
    """Derive a Spark StructType from a pandas DataFrame's dtypes.

    object-dtype and any unknown dtype maps to StringType, which is safe after
    sanitize_for_spark has converted all object columns to plain strings.
    """
    return StructType([
        StructField(str(col), _spark_type_for(dtype), nullable=True)
        for col, dtype in pdf.dtypes.items()
    ])


def sanitize_for_spark(pdf: pd.DataFrame) -> pd.DataFrame:
    """Stringify all object-dtype columns so the explicit schema is consistent.

    pybaseball returns object-dtype columns with mixed types across a full season.
    We stringify the entire object column for the bronze layer (type precision
    belongs in silver) and use pandas_schema_to_spark to pass an explicit schema
    to createDataFrame so Spark never attempts type inference from values.
    None/NaN are preserved as Python None so Spark maps them to null.
    """
    def _to_str_or_none(x: object) -> object:
        if x is None:
            return None
        try:
            if np.isnan(x):  # type: ignore[arg-type]
                return None
        except (TypeError, ValueError):
            pass
        return str(x)

    for col in pdf.select_dtypes(include="object").columns:
        pdf[col] = pdf[col].apply(_to_str_or_none)
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
