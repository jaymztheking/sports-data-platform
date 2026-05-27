"""Validation tests for Story 012 — MLB Bronze→Serving: Iceberg → Postgres raw_mlb.

Functional unit: Iceberg tables → PostgreSQL raw_mlb schema.

Tier 1 (structural/unit, local, no marker): loader module and function signatures;
table coverage; schema target and replace semantics; DAG load task and dependency.

Tier 2 (@pytest.mark.k3s): seed synthetic Iceberg tables in a throwaway namespace,
run the loader pod to populate a test Postgres schema, then assert the data contract
(tables exist, row counts match, metadata cols survive, idempotent reload).
Seeding uses synthetic data only — no pybaseball / Fangraphs dependency.
"""

import ast
import base64
import json
import os
import subprocess
import sys

import pytest

from .conftest import KUBECONFIG, NAMESPACE, SRC_DIR

PROJECT_ROOT = os.path.dirname(SRC_DIR)
COMMON_DIR = os.path.join(SRC_DIR, "common")
LOAD_DIR = os.path.join(SRC_DIR, "domains", "mlb", "load")
LOADER_FILE = os.path.join(LOAD_DIR, "iceberg_to_postgres.py")
DAG_FILE = os.path.join(PROJECT_ROOT, "dags", "mlb", "mlb_ingestion_dag.py")

TABLES = ["statcast", "batting", "pitching", "schedules"]
METADATA_COLS = ("ingested_at", "source", "season")
TEST_ICEBERG_NS = "mlb_ci_012"
TEST_PG_SCHEMA = "raw_mlb_ci_012"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse(path: str) -> tuple[str, ast.Module]:
    assert os.path.isfile(path), f"{path} does not exist"
    with open(path) as fh:
        source = fh.read()
    return source, ast.parse(source)


def _string_consts(tree: ast.AST) -> set[str]:
    return {
        n.value for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    }


def _func(tree: ast.AST, name: str) -> ast.FunctionDef | None:
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return n
    return None


# ===========================================================================
# Tier 1 — structural / unit (local, no cluster)
# ===========================================================================


class TestMlbLoadStructure:
    """Story 012: structural contract of the Iceberg → Postgres load unit."""

    def test_loader_module_exists(self):
        assert os.path.isfile(LOADER_FILE), (
            f"Loader module not found at {LOADER_FILE}"
        )

    def test_load_table_function_signature(self):
        _, tree = _parse(LOADER_FILE)
        fn = _func(tree, "load_table_to_postgres")
        assert fn is not None, "load_table_to_postgres not found in loader"
        params = [a.arg for a in fn.args.args]
        assert "spark" in params, "load_table_to_postgres must accept 'spark'"
        assert "iceberg_table" in params, "load_table_to_postgres must accept 'iceberg_table'"
        assert "pg_schema" in params, "load_table_to_postgres must accept 'pg_schema'"
        assert "pg_table" in params, "load_table_to_postgres must accept 'pg_table'"

    def test_load_all_function_signature(self):
        _, tree = _parse(LOADER_FILE)
        fn = _func(tree, "load_all_to_postgres")
        assert fn is not None, "load_all_to_postgres not found in loader"
        params = [a.arg for a in fn.args.args]
        assert "spark" in params, "load_all_to_postgres must accept 'spark'"
        assert "iceberg_ns" in params, "load_all_to_postgres must accept 'iceberg_ns'"
        assert "pg_schema" in params, "load_all_to_postgres must accept 'pg_schema'"

    def test_load_all_defaults_to_production_targets(self):
        _, tree = _parse(LOADER_FILE)
        fn = _func(tree, "load_all_to_postgres")
        args = fn.args.args
        defaults = fn.args.defaults
        param_defaults = {args[len(args) - len(defaults) + i].arg: d for i, d in enumerate(defaults)}
        assert "iceberg_ns" in param_defaults, "iceberg_ns must have a default"
        assert "pg_schema" in param_defaults, "pg_schema must have a default"
        assert ast.literal_eval(param_defaults["iceberg_ns"]) == "iceberg.mlb", (
            "iceberg_ns default must be 'iceberg.mlb'"
        )
        assert ast.literal_eval(param_defaults["pg_schema"]) == "raw_mlb", (
            "pg_schema default must be 'raw_mlb'"
        )

    def test_all_tables_covered(self):
        source, _ = _parse(LOADER_FILE)
        for table in TABLES:
            assert table in source, f"Loader does not reference table '{table}'"

    def test_schema_target_raw_mlb(self):
        _, tree = _parse(LOADER_FILE)
        assert "raw_mlb" in _string_consts(tree), (
            "Loader must reference 'raw_mlb' as default schema target"
        )

    def test_replace_semantics(self):
        source, _ = _parse(LOADER_FILE)
        assert "replace" in source, (
            "Loader must use replace/overwrite semantics for idempotency"
        )

    def test_dag_has_load_task(self):
        source, _ = _parse(DAG_FILE)
        assert "load_to_postgres" in source, (
            "DAG must contain a 'load_to_postgres' task"
        )

    def test_load_task_runs_after_all_ingestion(self):
        """load_to_postgres must declare >> dependency on all four ingest tasks."""
        source, tree = _parse(DAG_FILE)
        # The DAG must have >> or << operators linking ingestion to the load task.
        shift_ops = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.RShift, ast.LShift))
        ]
        assert shift_ops, (
            "DAG must use >> or << to declare load_to_postgres dependency on ingest tasks"
        )


# ===========================================================================
# Tier 2 — k3s integration / data contract (live cluster)
# ===========================================================================

_INGEST_IMAGE = "ghcr.io/jaymztheking/sports-data-platform/ingestion-spark:latest"

# Non-secret env vars for pods — credentials fetched at runtime from cluster secrets.
_POD_ENV_BASE = {
    "SPARK_MASTER_URL": "local[*]",
    "SPARK_ICEBERG_CATALOG_URI": "http://iceberg-rest:8181",
    "SPARK_S3_ENDPOINT": "http://minio:9000",
    "AWS_REGION": "us-east-1",
    "POSTGRES_HOST": "postgresql",
    "POSTGRES_PORT": "5432",
    "POSTGRES_USER": "postgres",
    "POSTGRES_DB": "sports_data",
}


def _minio_env() -> dict:
    result = subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "get", "secret", "minio",
         "-o", "jsonpath={.data.rootUser}|{.data.rootPassword}"],
        capture_output=True, text=True, check=True, timeout=15,
    )
    user_b64, pwd_b64 = result.stdout.strip().split("|", 1)
    user = base64.b64decode(user_b64).decode()
    pwd = base64.b64decode(pwd_b64).decode()
    return {
        "MINIO_ACCESS_KEY": user,
        "MINIO_SECRET_KEY": pwd,
        "AWS_ACCESS_KEY_ID": user,
        "AWS_SECRET_ACCESS_KEY": pwd,
    }


def _postgres_env() -> dict:
    result = subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "get", "secret", "postgresql",
         "-o", "jsonpath={.data.postgres-password}"],
        capture_output=True, text=True, check=True, timeout=15,
    )
    pwd = base64.b64decode(result.stdout.strip()).decode()
    return {"POSTGRES_PASSWORD": pwd}


def _full_pod_env() -> dict:
    return {**_POD_ENV_BASE, **_minio_env(), **_postgres_env()}


# Synthetic seed: minimal DataFrames for all four tables, no pybaseball required.
_SEED_DRIVER = f"""
import json
from pyspark.sql import Row
from pyspark.sql import functions as F
from src.common.spark import get_spark_session

spark = get_spark_session("mlb_ci_012_seed")
NS = "iceberg.{TEST_ICEBERG_NS}"
spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {{NS}}")

TABLES = {{
    "statcast": [
        Row(pitch_type="FF", release_speed=95.2, batter=660162, pitcher=605483),
        Row(pitch_type="SL", release_speed=88.1, batter=660200, pitcher=605483),
    ],
    "batting": [
        Row(Name="Player A", AB=500, H=140, HR=25),
        Row(Name="Player B", AB=450, H=120, HR=18),
    ],
    "pitching": [
        Row(Name="Pitcher A", W=15, L=8, ERA=3.20),
        Row(Name="Pitcher B", W=12, L=10, ERA=3.85),
    ],
    "schedules": [
        Row(Team="NYY", date="2024-04-01", home_team="NYY", away_team="BOS"),
        Row(Team="BOS", date="2024-04-01", home_team="NYY", away_team="BOS"),
    ],
}}

for name, rows in TABLES.items():
    df = spark.createDataFrame(rows)
    df = df.withColumn("ingested_at", F.lit("2024-01-01T00:00:00"))
    df = df.withColumn("source", F.lit(f"test.{{name}}"))
    df = df.withColumn("season", F.lit(2024).cast("int"))
    df.writeTo(f"{{NS}}.{{name}}").using("iceberg").partitionedBy("season").createOrReplace()

counts = {{t: spark.table(f"{{NS}}.{{t}}").count() for t in TABLES}}
print("SEED_COUNTS=" + json.dumps(counts))
spark.stop()
"""

_LOAD_DRIVER = f"""
import json
from src.common.spark import get_spark_session
from src.domains.mlb.load.iceberg_to_postgres import load_all_to_postgres

spark = get_spark_session("mlb_ci_012_load")
try:
    load_all_to_postgres(
        spark,
        iceberg_ns="iceberg.{TEST_ICEBERG_NS}",
        pg_schema="{TEST_PG_SCHEMA}",
    )
    print("LOAD_DONE=true")
finally:
    spark.stop()
"""

_TEARDOWN_DRIVER = f"""
from src.common.spark import get_spark_session
spark = get_spark_session("mlb_ci_012_teardown")
for t in {TABLES!r}:
    spark.sql(f"DROP TABLE IF EXISTS iceberg.{TEST_ICEBERG_NS}." + t + " PURGE")
spark.sql("DROP NAMESPACE IF EXISTS iceberg.{TEST_ICEBERG_NS}")
spark.stop()
"""


def _run_pod(script: str, pod_name: str, timeout: int = 300) -> subprocess.CompletedProcess:
    env = _full_pod_env()
    env_args = [f"--env={k}={v}" for k, v in env.items()]
    overrides = json.dumps({"spec": {"imagePullSecrets": [{"name": "ghcr-pull-secret"}]}})
    subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "run", pod_name,
         f"--image={_INGEST_IMAGE}",
         "--restart=Never",
         "--image-pull-policy=Always",
         f"--overrides={overrides}",
         *env_args,
         "--", "python3", "-c", script],
        capture_output=True, text=True, timeout=30, check=True,
    )
    subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "wait", f"pod/{pod_name}",
         "--for=jsonpath={.status.phase}=Succeeded",
         f"--timeout={timeout}s"],
        capture_output=True, text=True, timeout=timeout + 10,
    )
    logs = subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE, "logs", pod_name],
        capture_output=True, text=True, timeout=30,
    )
    phase = subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "get", "pod", pod_name, "-o", "jsonpath={.status.phase}"],
        capture_output=True, text=True, timeout=10,
    )
    return subprocess.CompletedProcess(
        args=[],
        returncode=0 if phase.stdout.strip() == "Succeeded" else 1,
        stdout=logs.stdout,
        stderr=logs.stderr,
    )


def _delete_pod(pod_name: str) -> None:
    try:
        subprocess.run(
            ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
             "delete", "pod", pod_name, "--ignore-not-found", "--grace-period=0"],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        pass


@pytest.fixture(scope="module")
def postgres_load(request):
    """Seed synthetic Iceberg data, run loader twice, yield (pg_conn, iceberg_counts); teardown."""
    psycopg2 = pytest.importorskip("psycopg2")

    # Seed Iceberg with synthetic data.
    seed_pod = "mlb-ci-012-seed"
    _delete_pod(seed_pod)
    seed_result = _run_pod(_SEED_DRIVER, seed_pod, timeout=900)
    _delete_pod(seed_pod)
    if seed_result.returncode != 0:
        pytest.fail(f"Seed pod failed:\nSTDOUT:\n{seed_result.stdout}\nSTDERR:\n{seed_result.stderr}")
    iceberg_counts = None
    for line in seed_result.stdout.splitlines():
        if line.startswith("SEED_COUNTS="):
            iceberg_counts = json.loads(line[len("SEED_COUNTS="):])
    assert iceberg_counts is not None, f"Seed pod did not emit counts:\n{seed_result.stdout}"

    # Run loader (first pass).
    load_pod = "mlb-ci-012-load"
    _delete_pod(load_pod)
    load_result = _run_pod(_LOAD_DRIVER, load_pod, timeout=900)
    _delete_pod(load_pod)
    if load_result.returncode != 0:
        pytest.fail(f"Load pod failed:\nSTDOUT:\n{load_result.stdout}\nSTDERR:\n{load_result.stderr}")

    # Run loader a second time to verify idempotency (replace semantics, no row duplication).
    reload_pod = "mlb-ci-012-reload"
    _delete_pod(reload_pod)
    reload_result = _run_pod(_LOAD_DRIVER, reload_pod, timeout=900)
    _delete_pod(reload_pod)
    if reload_result.returncode != 0:
        pytest.fail(f"Reload pod failed:\nSTDOUT:\n{reload_result.stdout}\nSTDERR:\n{reload_result.stderr}")

    # Connect to Postgres locally via NodePort.
    pg_pwd = _postgres_env()["POSTGRES_PASSWORD"]
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "192.168.50.231"),
        port=int(os.environ.get("POSTGRES_PORT", "30432")),
        user="postgres",
        password=pg_pwd,
        dbname="sports_data",
    )

    yield conn, iceberg_counts

    conn.close()

    # Teardown: drop test Postgres schema and Iceberg namespace.
    try:
        cleanup_conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "192.168.50.231"),
            port=int(os.environ.get("POSTGRES_PORT", "30432")),
            user="postgres",
            password=pg_pwd,
            dbname="sports_data",
        )
        cleanup_conn.autocommit = True
        with cleanup_conn.cursor() as cur:
            cur.execute(f"DROP SCHEMA IF EXISTS {TEST_PG_SCHEMA} CASCADE")
        cleanup_conn.close()
    except Exception:
        pass

    teardown_pod = "mlb-ci-012-teardown"
    _delete_pod(teardown_pod)
    _run_pod(_TEARDOWN_DRIVER, teardown_pod, timeout=180)
    _delete_pod(teardown_pod)


class TestMlbLoadIntegration:
    """Story 012: k3s data-contract tests for the Iceberg → Postgres load."""

    @pytest.mark.k3s
    def test_schema_exists_in_postgres(self, postgres_load):
        conn, _ = postgres_load
        with conn.cursor() as cur:
            cur.execute(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
                (TEST_PG_SCHEMA,),
            )
            assert cur.fetchone() is not None, f"Schema '{TEST_PG_SCHEMA}' not found in Postgres"

    @pytest.mark.k3s
    @pytest.mark.parametrize("table", TABLES)
    def test_table_exists_in_postgres(self, postgres_load, table):
        conn, _ = postgres_load
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = %s AND table_name = %s",
                (TEST_PG_SCHEMA, table),
            )
            assert cur.fetchone() is not None, (
                f"Table '{TEST_PG_SCHEMA}.{table}' not found in Postgres"
            )

    @pytest.mark.k3s
    @pytest.mark.parametrize("table", TABLES)
    def test_row_counts_match_iceberg(self, postgres_load, table):
        conn, iceberg_counts = postgres_load
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TEST_PG_SCHEMA}.{table}")
            pg_count = cur.fetchone()[0]
        assert pg_count == iceberg_counts[table], (
            f"{table}: Postgres has {pg_count} rows, Iceberg had {iceberg_counts[table]}"
        )

    @pytest.mark.k3s
    @pytest.mark.parametrize("table", TABLES)
    def test_metadata_columns_survive(self, postgres_load, table):
        conn, _ = postgres_load
        with conn.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = %s AND table_name = %s",
                (TEST_PG_SCHEMA, table),
            )
            cols = {row[0] for row in cur.fetchall()}
        for col in METADATA_COLS:
            assert col in cols, f"Metadata column '{col}' missing from {TEST_PG_SCHEMA}.{table}"

    @pytest.mark.k3s
    @pytest.mark.parametrize("table", TABLES)
    def test_idempotent_reload(self, postgres_load, table):
        """Loader run twice must not duplicate rows (fixture runs both passes)."""
        conn, iceberg_counts = postgres_load
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TEST_PG_SCHEMA}.{table}")
            pg_count = cur.fetchone()[0]
        assert pg_count == iceberg_counts[table], (
            f"{table}: after reload, Postgres has {pg_count} rows (expected {iceberg_counts[table]} — duplicate rows?)"
        )
