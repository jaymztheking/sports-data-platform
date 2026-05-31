output "airflow_url" {
  description = "Airflow webserver URL (set node_ip variable to a Pi node address)"
  value       = "http://${var.node_ip}:30007"
}

output "minio_console_url" {
  description = "MinIO console URL (set node_ip variable to a Pi node address)"
  value       = "http://${var.node_ip}:30090"
}

output "mlflow_url" {
  description = "MLflow tracking server URL (set node_ip variable to a Pi node address)"
  value       = "http://${var.node_ip}:30500"
}

output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.data_platform.metadata[0].name
}

output "portal_url" {
  description = "Sports Data Platform portal"
  value       = "http://sports.data"
}

output "airflow_dns_url" {
  description = "Airflow webserver (DNS)"
  value       = "http://airflow.sports.data"
}

output "minio_dns_url" {
  description = "MinIO console (DNS)"
  value       = "http://minio.sports.data"
}

output "spark_dns_url" {
  description = "Spark master UI (DNS)"
  value       = "http://spark.sports.data"
}

output "mlflow_dns_url" {
  description = "MLflow tracking server (DNS)"
  value       = "http://mlflow.sports.data"
}

output "iceberg_dns_url" {
  description = "Iceberg REST catalog (DNS)"
  value       = "http://iceberg.sports.data"
}
