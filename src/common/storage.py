import boto3
from mypy_boto3_s3.client import S3Client

from src.common.config import settings


def get_minio_client() -> S3Client:
    """Create a boto3 S3 client configured for MinIO."""
    cfg = settings.minio
    return boto3.client(
        "s3",
        endpoint_url=f"http{'s' if cfg.secure else ''}://{cfg.endpoint}",
        aws_access_key_id=cfg.access_key,
        aws_secret_access_key=cfg.secret_key,
    )
