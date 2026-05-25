"""Validation tests for Story 011 — MLB Bronze: pybaseball → Iceberg.

Functional unit: pybaseball → Iceberg tables in MinIO.

Tier 1 (structural/unit, local, no marker): `config`/`storage` via real import;
`spark`, the four ingestion modules, and the DAG via AST (pyspark/pybaseball/
pandas/airflow live only on the cluster images).

Tier 2 (`@pytest.mark.k3s`): micro-ingest all four tables into a throwaway
`iceberg.mlb_ci` namespace via an in-Airflow-pod driver, then assert the data
contract against the Iceberg REST catalog, MinIO, and captured row counts.
"""

import ast
import importlib.util
import inspect
import json
import os
import subprocess
import sys

import pytest

from .conftest import KUBECONFIG, NAMESPACE, SRC_DIR

PROJECT_ROOT = os.path.dirname(SRC_DIR)
COMMON_DIR = os.path.join(SRC_DIR, "common")
INGEST_DIR = os.path.join(SRC_DIR, "domains", "mlb", "ingestion")
DAG_FILE = os.path.join(PROJECT_ROOT, "dags", "mlb", "mlb_ingestion_dag.py")

ICEBERG_REST_URL = os.environ.get("ICEBERG_REST_URL", "http://192.168.50.231:30181")
WAREHOUSE_BUCKET = "spark-warehouse"
TEST_NS = "mlb_ci"

# module file -> (ingest fn, production table target)
INGEST_MODULES = {
    "statcast.py": ("ingest_statcast", "iceberg.mlb.statcast"),
    "batting.py": ("ingest_batting", "iceberg.mlb.batting"),
    "pitching.py": ("ingest_pitching", "iceberg.mlb.pitching"),
    "schedules.py": ("ingest_schedules", "iceberg.mlb.schedules"),
}
TABLES = ["statcast", "batting", "pitching", "schedules"]
METADATA_COLS = ("ingested_at", "source", "season")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load(module_key: str, directory: str, filename: str):
    """Real-import a module by file path, registering it under module_key."""
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    if module_key in sys.modules:
        return sys.modules[module_key]
    path = os.path.join(directory, filename)
    assert os.path.isfile(path), f"{path} does not exist"
    spec = importlib.util.spec_from_file_location(module_key, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[module_key] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


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


def _params_with_defaults(fn: ast.FunctionDef) -> dict[str, ast.expr]:
    args = fn.args.args
    defaults = fn.args.defaults
    return {args[len(args) - len(defaults) + i].arg: d for i, d in enumerate(defaults)}


def _withcolumn_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for n in ast.walk(tree):
        if (
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "withColumn"
            and n.args
            and isinstance(n.args[0], ast.Constant)
        ):
            names.add(n.args[0].value)
    return names


# ===========================================================================
# Tier 1 — structural / unit (local, no cluster)
# ===========================================================================


class TestMlbIngestStructure:
    """Story 011: structural contract of the pybaseball → Iceberg unit."""

    # ---- shared clients -------------------------------------------------

    def test_config_env_prefixes(self):
        mod = _load("src.common.config", COMMON_DIR, "config.py")
        assert mod.PostgresSettings.model_config["env_prefix"] == "POSTGRES_"
        assert mod.MinioSettings.model_config["env_prefix"] == "MINIO_"
        assert mod.SparkSettings.model_config["env_prefix"] == "SPARK_"

    def test_config_settings_singleton(self):
        mod = _load("src.common.config", COMMON_DIR, "config.py")
        for attr in ("postgres", "minio", "spark"):
            assert hasattr(mod.settings, attr), f"settings missing .{attr}"

    def test_spark_factory_signature(self):
        _, tree = _parse(os.path.join(COMMON_DIR, "spark.py"))
        fn = _func(tree, "get_spark_session")
        assert fn is not None, "get_spark_session not found"
        assert "app_name" in [a.arg for a in fn.args.args]

    def test_spark_iceberg_rest_config(self):
        _, tree = _parse(os.path.join(COMMON_DIR, "spark.py"))
        consts = _string_consts(tree)
        assert "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions" in consts
        assert "org.apache.iceberg.spark.SparkCatalog" in consts
        assert "rest" in consts
        assert "org.apache.iceberg.aws.s3.S3FileIO" in consts

    def test_spark_minio_s3a_config(self):
        _, tree = _parse(os.path.join(COMMON_DIR, "spark.py"))
        consts = _string_consts(tree)
        assert any("s3a.endpoint" in c for c in consts)
        assert any("s3a.access.key" in c for c in consts)
        assert any("s3a.secret.key" in c for c in consts)

    def test_storage_client_factory(self):
        _load("src.common.config", COMMON_DIR, "config.py")
        mod = _load("src.common.storage", COMMON_DIR, "storage.py")
        assert callable(getattr(mod, "get_minio_client", None))
        sig = inspect.signature(mod.get_minio_client)
        required = [p for p in sig.parameters.values() if p.default is inspect.Parameter.empty]
        assert not required, f"get_minio_client has required params: {required}"

    # ---- ingestion modules ---------------------------------------------

    @pytest.mark.parametrize("filename", list(INGEST_MODULES))
    def test_ingest_signature(self, filename):
        fn_name, _ = INGEST_MODULES[filename]
        _, tree = _parse(os.path.join(INGEST_DIR, filename))
        fn = _func(tree, fn_name)
        assert fn is not None, f"{fn_name} not found in {filename}"
        params = [a.arg for a in fn.args.args]
        assert params and params[0] == "spark", f"{fn_name} first param should be 'spark'"
        assert "table" in params, (
            f"{fn_name} must accept a 'table' param so the destination is overridable "
            f"(required for test-scoped micro-ingest)"
        )

    @pytest.mark.parametrize("filename", list(INGEST_MODULES))
    def test_ingest_table_default_is_production_target(self, filename):
        fn_name, target = INGEST_MODULES[filename]
        _, tree = _parse(os.path.join(INGEST_DIR, filename))
        fn = _func(tree, fn_name)
        defaults = _params_with_defaults(fn)
        assert "table" in defaults, f"{fn_name} 'table' param needs a default"
        assert ast.literal_eval(defaults["table"]) == target, (
            f"{fn_name} table default should be {target!r}"
        )

    @pytest.mark.parametrize("filename", list(INGEST_MODULES))
    def test_ingest_writes_to_table_param(self, filename):
        """writeTo() must use the `table` param, not a hardcoded literal."""
        source, tree = _parse(os.path.join(INGEST_DIR, filename))
        write_calls = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "writeTo"
        ]
        assert write_calls, f"{filename} has no writeTo() call"
        for call in write_calls:
            arg = call.args[0] if call.args else None
            assert isinstance(arg, ast.Name) and arg.id == "table", (
                f"{filename} writeTo() should be passed the `table` param, not a literal"
            )

    @pytest.mark.parametrize("filename", list(INGEST_MODULES))
    def test_ingest_fetch_function_exists(self, filename):
        _, tree = _parse(os.path.join(INGEST_DIR, filename))
        fetch = [n.name for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name.startswith("fetch_")]
        assert fetch, f"{filename} missing a fetch_* extract function"

    @pytest.mark.parametrize("filename", list(INGEST_MODULES))
    def test_ingest_metadata_contract(self, filename):
        _, tree = _parse(os.path.join(INGEST_DIR, filename))
        added = _withcolumn_names(tree)
        for col in METADATA_COLS:
            assert col in added, f"{filename} does not add .withColumn('{col}', ...)"

    @pytest.mark.parametrize("filename", list(INGEST_MODULES))
    def test_ingest_partitioned_by_season(self, filename):
        source, tree = _parse(os.path.join(INGEST_DIR, filename))
        assert "partitionedBy" in source, f"{filename} missing partitionedBy()"
        assert "season" in _string_consts(tree), f"{filename} not partitioned by season"

    # ---- schedules: 30-team source of truth ----------------------------

    def test_mlb_teams_constant(self):
        _, tree = _parse(os.path.join(INGEST_DIR, "schedules.py"))
        value = None
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "MLB_TEAMS" for t in n.targets
            ):
                value = n.value
            elif (
                isinstance(n, ast.AnnAssign)
                and isinstance(n.target, ast.Name)
                and n.target.id == "MLB_TEAMS"
                and n.value is not None
            ):
                value = n.value
        assert value is not None, "MLB_TEAMS not defined in schedules.py"
        teams = ast.literal_eval(value)
        assert len(teams) == 30 and len(set(teams)) == 30
        assert all(isinstance(t, str) and len(t) == 3 for t in teams)

    def test_schedules_teams_default_to_constant(self):
        _, tree = _parse(os.path.join(INGEST_DIR, "schedules.py"))
        fn = _func(tree, "ingest_schedules")
        defaults = _params_with_defaults(fn)
        assert "teams" in defaults, "ingest_schedules 'teams' has no default"
        d = defaults["teams"]
        assert isinstance(d, ast.Name) and d.id == "MLB_TEAMS", "teams should default to MLB_TEAMS"

    # ---- DAG -----------------------------------------------------------

    def _dag_decorator(self, tree):
        for n in ast.walk(tree):
            if isinstance(n, ast.FunctionDef):
                for dec in n.decorator_list:
                    if isinstance(dec, ast.Call) and getattr(dec.func, "id", "") == "dag":
                        return dec
        return None

    def test_dag_decorator_config(self):
        _, tree = _parse(DAG_FILE)
        dec = self._dag_decorator(tree)
        assert dec is not None, "no @dag decorator found"
        kw = {k.arg: k.value for k in dec.keywords}
        assert ast.literal_eval(kw["dag_id"]) == "mlb_ingestion"
        assert ast.literal_eval(kw["schedule"]) == "@weekly"
        assert ast.literal_eval(kw["catchup"]) is False
        tags = set(ast.literal_eval(kw["tags"]))
        assert {"mlb", "ingestion", "bronze"} <= tags

    def test_dag_has_four_ingestion_tasks(self):
        """Four KubernetesPodOperator calls — one per table — are present in the DAG."""
        source, _ = _parse(DAG_FILE)
        for table in ("ingest_statcast", "ingest_batting", "ingest_pitching", "ingest_schedules"):
            assert table in source, f"DAG missing call for task '{table}'"

    def test_ingestion_tasks_run_in_parallel(self):
        """The four ingestion tasks have no declared dependencies — fully parallel."""
        _, tree = _parse(DAG_FILE)
        deps = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.RShift, ast.LShift))
        ]
        assert not deps, (
            "ingestion tasks must not be chained with >>/<< — they run in parallel "
            f"(found {len(deps)} dependency operators)"
        )

    def test_dag_uses_mlb_teams_constant(self):
        """Schedules task script references MLB_TEAMS constant, not a hardcoded list."""
        source, tree = _parse(DAG_FILE)
        # MLB_TEAMS must appear somewhere in the DAG source (inline script or import).
        assert "MLB_TEAMS" in source, "DAG schedules task must reference MLB_TEAMS"
        # No top-level literal list of ≥30 team strings (would be a hardcoded duplicate).
        big_lists = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.List) and len(n.elts) >= 30
            and all(isinstance(e, ast.Constant) for e in n.elts)
        ]
        assert not big_lists, "DAG hardcodes a team list — use schedules.MLB_TEAMS instead"


# ===========================================================================
# Tier 2 — k3s integration / data contract (live cluster)
# ===========================================================================

pytest_k3s = pytest.mark.k3s

# ingestion-spark image: extends the Spark image with pybaseball/pydantic-settings/src/.
# src/ is at /app/src/ with PYTHONPATH=/app, so `from src.x import y` works directly.
_INGEST_IMAGE = "ghcr.io/jaymztheking/sports-data-platform/ingestion-spark:latest"
_INGEST_ENV = {
    "SPARK_MASTER_URL": "spark://spark-master-svc:7077",
    "SPARK_ICEBERG_CATALOG_URI": "http://iceberg-rest:8181",
    "SPARK_S3_ENDPOINT": "http://minio:9000",
    "MINIO_ACCESS_KEY": "minioadmin",
    "MINIO_SECRET_KEY": "minioadmin",
}

# Micro-ingests all four tables into the throwaway TEST_NS and prints a count line.
_INGEST_DRIVER = f"""
import json
from src.common.spark import get_spark_session
from src.domains.mlb.ingestion.statcast import ingest_statcast
from src.domains.mlb.ingestion.batting import ingest_batting
from src.domains.mlb.ingestion.pitching import ingest_pitching
from src.domains.mlb.ingestion.schedules import ingest_schedules

spark = get_spark_session("mlb_ci_micro_ingest")
spark.sql("CREATE NAMESPACE IF NOT EXISTS iceberg.{TEST_NS}")
try:
    ingest_statcast(spark, "2024-04-01", "2024-04-01", "iceberg.{TEST_NS}.statcast")
    ingest_batting(spark, 2024, "iceberg.{TEST_NS}.batting")
    ingest_pitching(spark, 2024, "iceberg.{TEST_NS}.pitching")
    ingest_schedules(spark, 2024, ["NYY", "BOS"], "iceberg.{TEST_NS}.schedules")
    counts = {{t: spark.table("iceberg.{TEST_NS}." + t).count()
              for t in {TABLES!r}}}
    print("MLB_CI_COUNTS=" + json.dumps(counts))
finally:
    spark.stop()
"""

_TEARDOWN_DRIVER = f"""
from src.common.spark import get_spark_session
spark = get_spark_session("mlb_ci_teardown")
for t in {TABLES!r}:
    spark.sql("DROP TABLE IF EXISTS iceberg.{TEST_NS}." + t + " PURGE")
spark.sql("DROP NAMESPACE IF EXISTS iceberg.{TEST_NS}")
spark.stop()
"""


def _run_in_ingestion_pod(script: str, pod_name: str, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a Python script in a temporary ingestion-spark pod and return its result."""
    env_args = [f"--env={k}={v}" for k, v in _INGEST_ENV.items()]
    # imagePullSecrets must be injected via --overrides since kubectl run has no --pull-secret flag.
    overrides = json.dumps({
        "spec": {"imagePullSecrets": [{"name": "ghcr-pull-secret"}]}
    })
    subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "run", pod_name,
         f"--image={_INGEST_IMAGE}",
         "--restart=Never",
         "--image-pull-policy=Always",
         f"--overrides={overrides}",
         *env_args,
         "--", "python", "-c", script],
        capture_output=True, text=True, timeout=30, check=True,
    )
    # Wait for the pod to finish (Succeeded or Failed).
    subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "wait", f"pod/{pod_name}",
         "--for=jsonpath={.status.phase}=Succeeded",
         f"--timeout={timeout}s"],
        capture_output=True, text=True, timeout=timeout + 10,
    )
    # Capture logs and exit code regardless of phase.
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
    subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "delete", "pod", pod_name, "--ignore-not-found"],
        capture_output=True, text=True, timeout=30,
    )


@pytest.fixture(scope="module")
def micro_ingest(request):
    """Run the all-four micro-ingest into mlb_ci; yield row counts; tear down."""
    pytest.importorskip("requests")  # REST assertions need it
    pod_name = "mlb-ci-micro-ingest"
    _delete_pod(pod_name)  # clean up any leftover from a prior run

    result = _run_in_ingestion_pod(_INGEST_DRIVER, pod_name)
    _delete_pod(pod_name)

    if result.returncode != 0:
        pytest.fail(
            f"micro-ingest driver failed:\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    counts = None
    for line in result.stdout.splitlines():
        if line.startswith("MLB_CI_COUNTS="):
            counts = json.loads(line[len("MLB_CI_COUNTS="):])
    assert counts is not None, f"driver did not emit counts:\n{result.stdout}"

    teardown_pod = "mlb-ci-teardown"

    def _teardown():
        _delete_pod(teardown_pod)
        _run_in_ingestion_pod(_TEARDOWN_DRIVER, teardown_pod, timeout=300)
        _delete_pod(teardown_pod)
    request.addfinalizer(_teardown)
    return counts


@pytest_k3s
class TestMlbIngestIntegration:
    """Story 011: pybaseball data actually lands in Iceberg with the right contract."""

    def test_namespace_created(self, micro_ingest, http):
        r = http.get(f"{ICEBERG_REST_URL}/v1/namespaces", timeout=15)
        assert r.status_code == 200
        flat = [ns for group in r.json().get("namespaces", []) for ns in group]
        assert TEST_NS in flat, f"{TEST_NS} namespace not in catalog: {flat}"

    def test_all_tables_exist(self, micro_ingest, http):
        r = http.get(f"{ICEBERG_REST_URL}/v1/namespaces/{TEST_NS}/tables", timeout=15)
        assert r.status_code == 200
        names = {t["name"] for t in r.json().get("identifiers", [])}
        for t in TABLES:
            assert t in names, f"table {TEST_NS}.{t} missing; got {names}"

    @pytest.mark.parametrize("table", TABLES)
    def test_schema_has_metadata_columns(self, micro_ingest, http, table):
        r = http.get(f"{ICEBERG_REST_URL}/v1/namespaces/{TEST_NS}/tables/{table}", timeout=15)
        assert r.status_code == 200, f"could not load {TEST_NS}.{table}"
        meta = r.json()["metadata"]
        schemas = {s["schema-id"]: s for s in meta["schemas"]}
        current = schemas[meta["current-schema-id"]]
        fields = {f["name"] for f in current["fields"]}
        for col in METADATA_COLS:
            assert col in fields, f"{TEST_NS}.{table} missing column '{col}'; got {fields}"

    @pytest.mark.parametrize("table", TABLES)
    def test_minio_has_data_and_season_partition(self, micro_ingest, s3_client, table):
        resp = s3_client.list_objects_v2(
            Bucket=WAREHOUSE_BUCKET, Prefix=f"{TEST_NS}/{table}/",
        )
        keys = [o["Key"] for o in resp.get("Contents", [])]
        assert keys, f"no objects under {WAREHOUSE_BUCKET}/{TEST_NS}/{table}/"
        assert any("/season=" in k for k in keys), (
            f"{TEST_NS}.{table} not partitioned by season in MinIO"
        )

    @pytest.mark.parametrize("table", TABLES)
    def test_row_counts_positive(self, micro_ingest, table):
        assert micro_ingest[table] > 0, f"{TEST_NS}.{table} ingested 0 rows"

    def test_dag_registered_and_importable(self):
        """DAG is importable and registered — checked via the Airflow scheduler pod."""
        for selector in ("component=scheduler", "component=triggerer"):
            r = subprocess.run(
                ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
                 "get", "pods", "-l", selector, "--field-selector=status.phase=Running",
                 "-o", "jsonpath={.items[0].metadata.name}"],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0 and r.stdout.strip():
                pod = r.stdout.strip()
                break
        else:
            pytest.skip("no running Airflow scheduler pod found")

        def _airflow(*args):
            return subprocess.run(
                ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
                 "exec", pod, "--", "airflow", *args],
                capture_output=True, text=True, timeout=120,
            )

        errors = _airflow("dags", "list-import-errors", "-o", "json")
        assert errors.returncode == 0, f"airflow CLI failed: {errors.stderr}"
        assert "mlb_ingestion" not in errors.stdout, f"DAG has import errors: {errors.stdout}"

        details = _airflow("dags", "details", "mlb_ingestion", "-o", "json")
        assert details.returncode == 0, f"mlb_ingestion not registered: {details.stderr}"
