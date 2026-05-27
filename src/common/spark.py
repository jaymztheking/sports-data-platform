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
    """Normalise a pybaseball DataFrame so PySpark can safely ingest it.

    Two-pass approach:
    1. Convert pandas nullable extension types (Int64, Float64, boolean) to numpy
       equivalents so pd.NA becomes NaN/None — PySpark's typed columns reject pd.NA.
    2. Stringify every remaining object-dtype column so the explicit schema derived
       by pandas_schema_to_spark only ever sees flat scalar types.

    None/NaN are preserved as Python None so Spark maps them to null.
    """
    _NULLABLE_INT = {"Int8", "Int16", "Int32", "Int64",
                     "UInt8", "UInt16", "UInt32", "UInt64"}
    _NULLABLE_FLOAT = {"Float32", "Float64"}

    # Pass 1: nullable extension types → numpy types (pd.NA → NaN)
    for col in pdf.columns:
        name = pdf[col].dtype.name
        if name in _NULLABLE_INT:
            pdf[col] = pdf[col].astype("float64")   # int+NA → float (NaN for missing)
        elif name in _NULLABLE_FLOAT:
            target = "float32" if name == "Float32" else "float64"
            pdf[col] = pdf[col].astype(target)
        elif name == "boolean":
            pdf[col] = pdf[col].astype(object)      # handled in pass 2

    # Pass 2: object columns → plain str (or None for missing)
    def _to_str_or_none(x):
        if x is None:
            return None
        try:
            if np.isnan(x):
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
        .config("spark.sql.catalog.iceberg.s3.region", "us-east-1")
        .config("spark.sql.defaultCatalog", "iceberg")
        .config("spark.hadoop.fs.s3a.endpoint", spark_cfg.s3_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", minio_cfg.access_key)
        .config("spark.hadoop.fs.s3a.secret.key", minio_cfg.secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )
