from sqlalchemy import create_engine, Engine

from src.common.config import settings


def get_engine() -> Engine:
    """Create a SQLAlchemy engine for the sports_data PostgreSQL database."""
    return create_engine(settings.postgres.url)
