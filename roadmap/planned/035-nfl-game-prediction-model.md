# NFL Game Winner Prediction Model

**Phase**: 5 — ML Pipeline
**Story Points**: 5

## User Story
As a data scientist, I want an NFL game winner classification model tracked in MLflow so that I can predict game outcomes based on team season stats.

## Acceptance Criteria
- [ ] `src/domains/nfl/ml/features.py` queries NFL gold tables, builds team-level feature matrix
- [ ] `src/domains/nfl/ml/models/game_prediction.py` trains XGBoost classifier
- [ ] Training logs params, metrics (accuracy, precision, recall, AUC), and model to MLflow
- [ ] Evaluation step tags model quality
- [ ] `dags/nfl/nfl_ml_dag.py` orchestrates build_features → train → evaluate
- [ ] MLflow experiment visible with logged runs
