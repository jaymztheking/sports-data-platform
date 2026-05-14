.PHONY: install lint test dbt-run dbt-test tf-init tf-plan tf-apply build-images

install:
	uv sync --all-extras

lint:
	uv run ruff check src/ tests/
	uv run mypy src/

test:
	uv run pytest tests/

dbt-compile:
	cd dbt_project && uv run dbt compile

dbt-run:
	cd dbt_project && uv run dbt run

dbt-test:
	cd dbt_project && uv run dbt test

tf-init:
	cd infra/terraform && terraform init

tf-plan:
	cd infra/terraform && terraform plan

tf-apply:
	cd infra/terraform && terraform apply

build-images:
	docker build -t ghcr.io/jamesmedaugh/sports-data-platform/airflow:latest -f docker/airflow/Dockerfile .
	docker build -t ghcr.io/jamesmedaugh/sports-data-platform/spark:latest -f docker/spark/Dockerfile .
	docker build -t ghcr.io/jamesmedaugh/sports-data-platform/mlflow:latest -f docker/mlflow/Dockerfile .
	docker build -t ghcr.io/jamesmedaugh/sports-data-platform/ingestion:latest -f docker/ingestion/Dockerfile .
