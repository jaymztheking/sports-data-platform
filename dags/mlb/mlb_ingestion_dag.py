"""MLB Bronze Layer Ingestion DAG.

Each task runs in a dedicated ingestion-spark pod (KubernetesPodOperator).
The pod image has Java, the Iceberg JARs, and all Python deps baked in.
Airflow is a pure orchestrator — no Spark or Java needed in the Airflow image.
"""

from datetime import datetime

from airflow.decorators import dag
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s

_IMAGE = "ghcr.io/jaymztheking/sports-data-platform/ingestion-spark:latest"
_NAMESPACE = "data-platform"
_PULL_SECRETS = [k8s.V1LocalObjectReference(name="ghcr-pull-secret")]

# Env vars the ingestion-spark image reads via src/common/config.py (pydantic-settings).
_ENV = [
    k8s.V1EnvVar(name="SPARK_MASTER_URL", value="spark://spark-master-svc:7077"),
    k8s.V1EnvVar(name="SPARK_ICEBERG_CATALOG_URI", value="http://iceberg-rest:8181"),
    k8s.V1EnvVar(name="SPARK_S3_ENDPOINT", value="http://minio:9000"),
    k8s.V1EnvVar(name="MINIO_ACCESS_KEY", value="minioadmin"),
    k8s.V1EnvVar(name="MINIO_SECRET_KEY", value="minioadmin"),
]


def _pod(task_id: str, script: str) -> KubernetesPodOperator:
    return KubernetesPodOperator(
        task_id=task_id,
        name=f"mlb-ingest-{task_id.replace('_', '-')}",
        namespace=_NAMESPACE,
        image=_IMAGE,
        image_pull_policy="Always",
        image_pull_secrets=_PULL_SECRETS,
        env_vars=_ENV,
        cmds=["python3", "-c"],
        arguments=[script],
        in_cluster=True,
        is_delete_operator_pod=True,
        get_logs=True,
    )


@dag(
    dag_id="mlb_ingestion",
    schedule="@weekly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["mlb", "ingestion", "bronze"],
)
def mlb_ingestion():
    ingest_statcast = _pod("ingest_statcast", """\
from src.common.spark import get_spark_session
from src.domains.mlb.ingestion.statcast import ingest_statcast
spark = get_spark_session("mlb_statcast_ingestion")
try:
    ingest_statcast(spark, "2024-03-28", "2024-09-29")
finally:
    spark.stop()
""")

    ingest_batting = _pod("ingest_batting", """\
from src.common.spark import get_spark_session
from src.domains.mlb.ingestion.batting import ingest_batting
spark = get_spark_session("mlb_batting_ingestion")
try:
    ingest_batting(spark, 2024)
finally:
    spark.stop()
""")

    ingest_pitching = _pod("ingest_pitching", """\
from src.common.spark import get_spark_session
from src.domains.mlb.ingestion.pitching import ingest_pitching
spark = get_spark_session("mlb_pitching_ingestion")
try:
    ingest_pitching(spark, 2024)
finally:
    spark.stop()
""")

    ingest_schedules = _pod("ingest_schedules", """\
from src.common.spark import get_spark_session
from src.domains.mlb.ingestion.schedules import MLB_TEAMS, ingest_schedules
spark = get_spark_session("mlb_schedules_ingestion")
try:
    ingest_schedules(spark, 2024, MLB_TEAMS)
finally:
    spark.stop()
""")

    load_to_postgres = _pod("load_to_postgres", """\
from src.common.spark import get_spark_session
from src.domains.mlb.load.iceberg_to_postgres import load_all_to_postgres
spark = get_spark_session("mlb_load_to_postgres")
try:
    load_all_to_postgres(spark)
finally:
    spark.stop()
""")

    [ingest_statcast, ingest_batting, ingest_pitching, ingest_schedules] >> load_to_postgres


mlb_ingestion()
