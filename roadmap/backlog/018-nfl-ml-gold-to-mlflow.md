# NFL ML: gold tables → game-winner model in MLflow

**Phase**: 5 — ML Pipeline
**Functional unit**: NFL gold tables → trained classifier + run logged in MLflow

## User Story
As a data scientist, I want an NFL game-winner classifier trained from the gold layer and tracked in MLflow so that I can predict outcomes from team season stats.

## Scope
One hop: gold → MLflow. Owns NFL feature building, model training/evaluation, and the NFL ML DAG.

## Acceptance Criteria

### Implementation
- [ ] `src/domains/nfl/ml/features.py` builds a team-level feature matrix from NFL gold tables
- [ ] `game_prediction.py` trains an XGBoost classifier
- [ ] training logs params, metrics (accuracy, precision, recall, AUC), and model to MLflow
- [ ] evaluation step tags model quality
- [ ] NFL ML DAG orchestrates build_features → train → evaluate

### Validation — unit / structural
- [ ] feature/training/evaluate signatures and MLflow logging calls; DAG wiring

### Validation — k3s integration / data contract
- [ ] DAG run completes against real gold data
- [ ] MLflow experiment shows a run with classification metrics logged
- [ ] model artifact stored in MinIO `mlflow-artifacts`
- [ ] at least one run carries a quality tag

## Definition of Done
Unit tests pass locally and the k3s integration class passes against the live cluster.
