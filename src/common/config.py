from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    model_config = {"env_prefix": "POSTGRES_"}

    host: str = "localhost"
    port: int = 5432
    user: str = "sports_data"
    password: str = "changeme"
    db: str = "sports_data"

    @property
    def url(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class MinioSettings(BaseSettings):
    model_config = {"env_prefix": "MINIO_"}

    endpoint: str = "localhost:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    secure: bool = False


class SparkSettings(BaseSettings):
    model_config = {"env_prefix": "SPARK_"}

    master_url: str = "spark://localhost:7077"
    iceberg_catalog_uri: str = "http://localhost:8181"
    s3_endpoint: str = "http://localhost:9000"


class Settings(BaseSettings):
    postgres: PostgresSettings = PostgresSettings()
    minio: MinioSettings = MinioSettings()
    spark: SparkSettings = SparkSettings()


settings = Settings()
