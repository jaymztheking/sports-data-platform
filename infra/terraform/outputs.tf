output "airflow_url" {
  description = "Airflow webserver URL"
  value       = "http://<node-ip>:${var.namespace == "data-platform" ? "30080" : "30080"}"
}

output "minio_console_url" {
  description = "MinIO console URL"
  value       = "http://<node-ip>:30090"
}

output "mlflow_url" {
  description = "MLflow tracking server URL"
  value       = "http://<node-ip>:30500"
}

output "namespace" {
  description = "Kubernetes namespace"
  value       = kubernetes_namespace.data_platform.metadata[0].name
}
