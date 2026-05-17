output "airflow_url" {
  description = "Airflow webserver URL (set node_ip variable to a Pi node address)"
  value       = "http://${var.node_ip}:30080"
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
