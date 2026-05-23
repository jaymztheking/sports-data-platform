.PHONY: install lint test dbt-run dbt-test tf-init tf-plan tf-apply build-images build-spark build-airflow

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

build-spark:
	docker build -t jaymztheking/spark:latest -f docker/spark/Dockerfile .
	docker push jaymztheking/spark:latest

build-airflow:
	docker buildx build --platform linux/arm64 -t jaymztheking/airflow:latest -f docker/airflow/Dockerfile . --push

build-images: build-spark build-airflow
