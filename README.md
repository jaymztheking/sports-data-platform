# Sports Data Platform

Modern data platform for sports analytics across NFL, MLB, NBA, and NHL, built on a medallion architecture with data mesh domain separation.

## Architecture

```
  MacBook Air (dev)                    K3s Cluster (6x Raspberry Pi, ARM64)
  ┌──────────────────┐    git push     ┌─────────────────────────────────────────┐
  │ Python code      │───────────────> │ GitHub Actions (self-hosted runner)     │
  │ dbt models       │                 │   └─ terraform apply                   │
  │ Terraform configs│                 │                                         │
  └──────────────────┘                 │ Services:                               │
                                       │  ├── PostgreSQL (silver/gold + meta)    │
                                       │  ├── MinIO (bronze object storage)      │
                                       │  ├── Iceberg REST Catalog               │
                                       │  ├── Spark (master + workers)           │
                                       │  ├── Airflow (webserver + scheduler)    │
                                       │  └── MLflow (tracking server)           │
                                       └─────────────────────────────────────────┘
```

**Data Flow**: APIs (pybaseball, etc.) → PySpark → Iceberg/MinIO → Loader → Postgres → dbt → Gold tables → MLflow

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | Apache Airflow |
| Ingestion | PySpark + pybaseball/nfl-data-py/nba-api |
| Bronze Storage | Apache Iceberg on MinIO |
| Transformation | dbt (PostgreSQL) |
| Serving | PostgreSQL |
| ML | MLflow + XGBoost |
| Infrastructure | K3s, Terraform, Helm |
| CI/CD | GitHub Actions (self-hosted ARM64 runner) |

## Quick Start

```bash
# Install dependencies
make install

# Run linting
make lint

# Run tests
make test

# Deploy infrastructure (requires K3s cluster)
make tf-init
make tf-plan
make tf-apply
```

See [docs/services.md](docs/services.md) for all cluster service URLs and credentials.

## Project Structure

```
├── infra/terraform/     # Terraform configs for K3s deployment
├── infra/helm-values/   # Helm chart value overrides
├── docker/              # Custom Docker images (ARM64)
├── src/common/          # Shared config, Spark, Postgres, MinIO utilities
├── src/domains/mlb/     # MLB ingestion, loaders, ML
├── src/domains/nfl/     # NFL (planned)
├── src/domains/nba/     # NBA (planned)
├── src/domains/nhl/     # NHL (planned)
├── dags/                # Airflow DAGs per sport
├── dbt_project/         # dbt models (staging → marts)
└── tests/               # Unit and integration tests
```

## Sports Domains

- **MLB** (active): Statcast, batting/pitching stats, schedules via pybaseball
- **NFL** (planned): Play-by-play, weekly stats via nfl-data-py
- **NBA** (planned): Player stats, game logs via nba-api
- **NHL** (planned): Game/player stats via nhl-api-py
