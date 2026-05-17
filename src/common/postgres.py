from sqlalchemy import Engine, create_engine

from src.common.config import settings


def get_engine() -> Engine:
    """Create a SQLAlchemy engine for the sports_data PostgreSQL database."""
    return create_engine(settings.postgres.url)
