# MLB ML: gold tables → pitcher model in MLflow

**Phase**: 5 — ML Pipeline
**Functional unit**: gold pitching tables → trained model + run logged in MLflow (artifact in MinIO)

## User Story
As a data scientist, I want a pitcher strikeout projection model trained from the gold layer and tracked in MLflow so that I can train, evaluate, and compare runs with real data.

## Scope
One hop: gold → MLflow. Owns feature building, model training/evaluation, and the ML DAG that orchestrates it.

## Acceptance Criteria

### Implementation
- [ ] `features.py` queries gold pitching tables, computes lag features (prev-season stats), persists feature matrix
- [ ] `pitcher_projections.py` trains an XGBoost regressor with configurable hyperparameters
- [ ] training logs params, metrics (RMSE, MAE, R²), and the model artifact to MLflow
- [ ] `evaluate()` tags run quality against an R² threshold
- [ ] ML DAG orchestrates build_features → train → evaluate

### Validation — unit / structural
- [ ] feature/training/evaluate function signatures and MLflow logging calls present
- [ ] DAG task wiring (build_features → train → evaluate)

### Validation — k3s integration / data contract
- [ ] DAG run completes against real gold data
- [ ] an MLflow experiment shows a run with logged params and metrics (RMSE, MAE, R²)
- [ ] model artifact stored in MinIO `mlflow-artifacts` bucket
- [ ] at least one run carries a quality tag

## Definition of Done
Unit tests pass locally and the k3s integration class passes against the live cluster.
