"""Shared Airflow task groups for common patterns across sports domains."""

from airflow.decorators import task


@task
def dbt_run(select: str) -> None:
    """Run dbt models with a given selector."""
    import subprocess

    subprocess.run(
        ["dbt", "run", "--select", select, "--project-dir", "/opt/dbt_project"],
        check=True,
    )


@task
def dbt_test(select: str) -> None:
    """Run dbt tests with a given selector."""
    import subprocess

    subprocess.run(
        ["dbt", "test", "--select", select, "--project-dir", "/opt/dbt_project"],
        check=True,
    )
