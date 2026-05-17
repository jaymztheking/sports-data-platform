from typing import Any

import boto3

from src.common.config import settings


def get_minio_client() -> Any:
    """Create a boto3 S3 client configured for MinIO."""
    cfg = settings.minio
    return boto3.client(
        "s3",
        endpoint_url=f"http{'s' if cfg.secure else ''}://{cfg.endpoint}",
        aws_access_key_id=cfg.access_key,
        aws_secret_access_key=cfg.secret_key,
    )
