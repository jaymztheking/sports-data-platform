resource "helm_release" "minio" {
  name       = "minio"
  namespace  = kubernetes_namespace.data_platform.metadata[0].name
  repository = "https://charts.min.io/"
  chart      = "minio"
  version    = "5.2.0"

  values = [file("${path.module}/../helm-values/minio-values.yaml")]

  set_sensitive {
    name  = "rootPassword"
    value = var.minio_root_password
  }
}
