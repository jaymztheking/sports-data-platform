"""Shared fixtures for validation tests."""

import os
import subprocess

import pytest

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INFRA_DIR = os.path.join(PROJECT_ROOT, "infra")
TERRAFORM_DIR = os.path.join(INFRA_DIR, "terraform")
HELM_VALUES_DIR = os.path.join(INFRA_DIR, "helm-values")
DOCKER_DIR = os.path.join(PROJECT_ROOT, "docker")
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
DAGS_DIR = os.path.join(PROJECT_ROOT, "dags")
DBT_DIR = os.path.join(PROJECT_ROOT, "dbt_project")
GITHUB_DIR = os.path.join(PROJECT_ROOT, ".github")

NAMESPACE = os.environ.get("K8S_NAMESPACE", "data-platform")
KUBECONFIG = os.environ.get("KUBECONFIG", os.path.expanduser("~/.kube/config"))

# ---------------------------------------------------------------------------
# Cluster connectivity helpers
# ---------------------------------------------------------------------------


def _kubectl(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a kubectl command and return the CompletedProcess."""
    cmd = ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE, *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _kubectl_get_json(resource: str, name: str = "") -> dict:
    """Return parsed JSON from kubectl get."""
    import json

    parts = ["get", resource]
    if name:
        parts.append(name)
    parts += ["-o", "json"]
    result = _kubectl(*parts)
    result.check_returncode()
    return json.loads(result.stdout)


@pytest.fixture()
def kubectl():
    """Expose the _kubectl helper as a fixture."""
    return _kubectl


@pytest.fixture()
def kubectl_json():
    """Expose the _kubectl_get_json helper as a fixture."""
    return _kubectl_get_json


# ---------------------------------------------------------------------------
# Postgres connection fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def pg_conn():
    """Return a psycopg2 connection to the platform PostgreSQL.

    Reads env vars: POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD.
    """
    psycopg2 = pytest.importorskip("psycopg2")
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "192.168.50.231"),
        port=int(os.environ.get("POSTGRES_PORT", "30432")),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "changeme"),
        dbname=os.environ.get("POSTGRES_DB", "sports_data"),
    )
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# MinIO / S3 client fixture
# ---------------------------------------------------------------------------


def _minio_password() -> str:
    """Return MinIO root password from env var or K8s secret."""
    if pw := os.environ.get("MINIO_ROOT_PASSWORD"):
        return pw
    result = subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "get", "secret", "minio", "-o", "jsonpath={.data.rootPassword}"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode == 0 and result.stdout.strip():
        import base64
        return base64.b64decode(result.stdout.strip()).decode()
    return "minioadmin"


@pytest.fixture()
def s3_client():
    """Return a boto3 S3 client configured for MinIO."""
    boto3 = pytest.importorskip("boto3")
    client = boto3.client(
        "s3",
        endpoint_url=os.environ.get("MINIO_ENDPOINT", "http://192.168.50.231:30900"),
        aws_access_key_id=os.environ.get("MINIO_ROOT_USER", "minioadmin"),
        aws_secret_access_key=_minio_password(),
    )
    return client


# ---------------------------------------------------------------------------
# HTTP session fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def http():
    """Return a requests.Session for health-check probes."""
    requests = pytest.importorskip("requests")
    session = requests.Session()
    session.timeout = 10
    yield session
    session.close()
