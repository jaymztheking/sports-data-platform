"""MLB Machine Learning DAG.

Builds features, trains models, and logs to MLflow.
"""

from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="mlb_ml",
    schedule=None,  # Triggered after transform
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["mlb", "ml"],
)
def mlb_ml():
    @task
    def build_features() -> str:
        from src.domains.mlb.ml.features import build_pitcher_features

        path = build_pitcher_features()
        return path

    @task
    def train_model(features_path: str) -> str:
        from src.domains.mlb.ml.models.pitcher_projections import train

        run_id = train(features_path)
        return run_id

    @task
    def evaluate(run_id: str) -> None:
        from src.domains.mlb.ml.models.pitcher_projections import evaluate

        evaluate(run_id)

    features = build_features()
    run_id = train_model(features)
    evaluate(run_id)


mlb_ml()
