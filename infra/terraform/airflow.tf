resource "helm_release" "airflow" {
  name       = "airflow"
  namespace  = kubernetes_namespace.data_platform.metadata[0].name
  repository = "https://airflow.apache.org"
  chart      = "airflow"
  version    = "1.14.0"
  timeout    = 900

  values = [file("${path.module}/../helm-values/airflow-values.yaml")]

  set {
    name  = "images.airflow.repository"
    value = "${var.image_registry}/airflow"
  }

  set {
    name  = "images.airflow.tag"
    value = var.airflow_image_tag
  }

  set {
    name  = "images.airflow.pullPolicy"
    value = "Always"
  }

  set {
    name  = "imagePullSecrets[0].name"
    value = kubernetes_secret.ghcr_pull_secret.metadata[0].name
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
