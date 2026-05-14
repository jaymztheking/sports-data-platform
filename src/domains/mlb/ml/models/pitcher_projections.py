"""Pitcher strikeout projection model using XGBoost, tracked with MLflow."""

import mlflow
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

FEATURE_COLS = [
    "prev_strikeouts",
    "prev_k_per_9",
    "prev_ip",
    "prev_era",
    "prev_fip",
    "innings_pitched",
]
TARGET_COL = "strikeouts"

PARAMS = {
    "n_estimators": 200,
    "max_depth": 6,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42,
}


def train(features_path: str) -> str:
    """Train pitcher strikeout projection model. Returns MLflow run ID."""
    df = pd.read_parquet(features_path)
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    mlflow.set_experiment("mlb_pitcher_strikeout_projection")

    with mlflow.start_run() as run:
        mlflow.log_params(PARAMS)

        model = xgb.XGBRegressor(**PARAMS)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        metrics = {
            "rmse": mean_squared_error(y_test, y_pred, squared=False),
            "mae": mean_absolute_error(y_test, y_pred),
            "r2": r2_score(y_test, y_pred),
        }
        mlflow.log_metrics(metrics)
        mlflow.xgboost.log_model(model, artifact_path="model")

        return run.info.run_id


def evaluate(run_id: str) -> None:
    """Load a trained model and log additional evaluation artifacts."""
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    metrics = run.data.metrics

    if metrics.get("r2", 0) > 0.5:
        client.set_tag(run_id, "model_quality", "good")
    else:
        client.set_tag(run_id, "model_quality", "needs_improvement")
