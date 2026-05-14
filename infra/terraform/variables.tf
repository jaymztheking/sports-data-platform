variable "kubeconfig_path" {
  description = "Path to the kubeconfig file for the K3s cluster"
  type        = string
  default     = "~/.kube/config"
}

variable "namespace" {
  description = "Kubernetes namespace for all data platform services"
  type        = string
  default     = "data-platform"
}

variable "postgres_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "minio_root_password" {
  description = "MinIO root password"
  type        = string
  sensitive   = true
}

variable "airflow_fernet_key" {
  description = "Airflow Fernet key for encrypting connections"
  type        = string
  sensitive   = true
}

variable "image_registry" {
  description = "Container image registry prefix"
  type        = string
  default     = "ghcr.io/jamesmedaugh/sports-data-platform"
}

variable "spark_image_tag" {
  description = "Tag for the custom Spark image"
  type        = string
  default     = "latest"
}

variable "airflow_image_tag" {
  description = "Tag for the custom Airflow image"
  type        = string
  default     = "latest"
}

variable "mlflow_image_tag" {
  description = "Tag for the custom MLflow image"
  type        = string
  default     = "latest"
}
