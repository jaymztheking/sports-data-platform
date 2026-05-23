resource "helm_release" "airflow" {
  name       = "airflow"
  namespace  = kubernetes_namespace.data_platform.metadata[0].name
  repository = "https://airflow.apache.org"
  chart      = "airflow"
  version    = "1.14.0"
  timeout    = 900

  values = [file("${path.module}/../helm-values/airflow-values.yaml")]

  # Stock apache/airflow image (ARM64-compatible). Switch to custom image
  # once story 009 (ARM64 CI build + Docker Hub push) is complete.
  set {
    name  = "images.airflow.repository"
    value = "apache/airflow"
  }

  set {
    name  = "images.airflow.tag"
    value = "2.9.3-python3.11"
  }

  set_sensitive {
    name  = "fernetKey"
    value = var.airflow_fernet_key
  }

  set_sensitive {
    name  = "data.metadataConnection.pass"
    value = var.postgres_password
  }

  depends_on = [helm_release.postgresql, helm_release.minio]
}
