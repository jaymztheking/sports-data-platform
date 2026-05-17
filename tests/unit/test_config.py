"""Tests for configuration module."""

from src.common.config import MinioSettings, PostgresSettings


def test_postgres_settings_defaults():
    settings = PostgresSettings()
    assert settings.host == "localhost"
    assert settings.port == 5432
    assert "postgresql+psycopg2" in settings.url


def test_minio_settings_defaults():
    settings = MinioSettings()
    assert settings.endpoint == "localhost:9000"
    assert settings.secure is False
