"""MLB Silver/Gold Layer Transform DAG.

Runs dbt models to transform raw MLB data through staging to marts.
"""

from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="mlb_transform",
    schedule=None,  # Triggered after ingestion
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["mlb", "transform", "dbt"],
)
def mlb_transform():
    @task
    def dbt_staging() -> None:
        import subprocess

        subprocess.run(
            ["dbt", "run", "--select", "tag:mlb,tag:staging", "--project-dir", "/opt/dbt_project"],
            check=True,
        )

    @task
    def dbt_marts() -> None:
        import subprocess

        subprocess.run(
            ["dbt", "run", "--select", "tag:mlb,tag:marts", "--project-dir", "/opt/dbt_project"],
            check=True,
        )

    @task
    def dbt_test() -> None:
        import subprocess

        subprocess.run(
            ["dbt", "test", "--select", "tag:mlb", "--project-dir", "/opt/dbt_project"],
            check=True,
        )

    staging = dbt_staging()
    marts = dbt_marts()
    test = dbt_test()

    staging >> marts >> test


mlb_transform()
