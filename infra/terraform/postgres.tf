resource "kubernetes_config_map" "postgres_init" {
  metadata {
    name      = "postgres-init-scripts"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }

  data = {
    "init.sql" = <<-SQL
      CREATE DATABASE airflow;
      CREATE DATABASE mlflow;
    \c sports_data
      CREATE SCHEMA IF NOT EXISTS raw_mlb;
      CREATE SCHEMA IF NOT EXISTS raw_nfl;
      CREATE SCHEMA IF NOT EXISTS raw_nba;
      CREATE SCHEMA IF NOT EXISTS raw_nhl;
      CREATE SCHEMA IF NOT EXISTS staging;
      CREATE SCHEMA IF NOT EXISTS marts;
    SQL
  }
}

resource "helm_release" "postgresql" {
  name       = "postgresql"
  namespace  = kubernetes_namespace.data_platform.metadata[0].name
  repository = "oci://registry-1.docker.io/bitnamicharts"
  chart      = "postgresql"
  version    = "18.6.6"

  values = [file("${path.module}/../helm-values/postgres-values.yaml")]

  set_sensitive {
    name  = "auth.postgresPassword"
    value = var.postgres_password
  }

  set {
    name  = "primary.initdb.scriptsConfigMap"
    value = kubernetes_config_map.postgres_init.metadata[0].name
  }
}
