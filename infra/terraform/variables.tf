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
  description = "Container image registry prefix (e.g. ghcr.io/owner/repo)"
  type        = string
  default     = "ghcr.io/jaymztheking/sports-data-platform"
}

variable "ghcr_token" {
  description = "GitHub PAT with read:packages scope — used to create the GHCR imagePullSecret. Omit if GHCR packages are public."
  type        = string
  sensitive   = true
  default     = ""
}

variable "spark_image_tag" {
  description = "Tag for the custom Spark image"
  type        = string
  default     = "latest"
}

variable "airflow_image_tag" {
  description = "Tag for the custom Airflow image"
  type        = string
  default     = "88065c45aa7339d0ac640aea41810ab3527a4052"
}

variable "mlflow_image_tag" {
  description = "Tag for the custom MLflow image"
  type        = string
  default     = "latest"
}

variable "node_ip" {
  description = "IP address of any K3s node (used to construct NodePort service URLs in outputs)"
  type        = string
  default     = "NODE_IP"
}
