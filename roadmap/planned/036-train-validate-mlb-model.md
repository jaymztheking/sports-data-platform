# Train and Validate MLB Pitcher Model

**Phase**: 5 — ML Pipeline
**Story Points**: 3

## User Story
As a data scientist, I want to run the MLB ML DAG end-to-end so that a trained pitcher projection model is logged in MLflow with real data.

## Acceptance Criteria
- [ ] MLB ML DAG triggerable from Airflow UI
- [ ] Feature matrix built from gold pitching tables
- [ ] XGBoost model trained with logged hyperparameters
- [ ] Metrics (RMSE, MAE, R2) visible in MLflow UI
- [ ] Model artifact stored in MinIO `mlflow-artifacts` bucket
- [ ] At least one run tagged with model quality assessment
