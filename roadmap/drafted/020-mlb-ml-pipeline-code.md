# MLB ML Pipeline Code

**Phase**: 5 — ML Pipeline
**Story Points**: 5

## User Story
As a data scientist, I want a pitcher strikeout projection model with MLflow tracking so that I can train, evaluate, and compare model runs.

## Acceptance Criteria
- [x] `features.py` queries gold pitching tables, computes lag features (prev season stats), saves to parquet
- [x] `pitcher_projections.py` trains XGBoost regressor with configurable hyperparameters
- [x] Training logs params, metrics (RMSE, MAE, R2), and model artifact to MLflow
- [x] `evaluate()` tags run quality based on R2 threshold
- [x] `mlb_ml_dag.py` orchestrates build_features → train → evaluate in Airflow
