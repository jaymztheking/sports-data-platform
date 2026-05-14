resource "helm_release" "spark" {
  name       = "spark"
  namespace  = kubernetes_namespace.data_platform.metadata[0].name
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "spark"
  version    = "9.2.0"

  values = [file("${path.module}/../helm-values/spark-values.yaml")]

  set {
    name  = "image.repository"
    value = "${var.image_registry}/spark"
  }

  set {
    name  = "image.tag"
    value = var.spark_image_tag
  }

  depends_on = [helm_release.minio, kubernetes_deployment.iceberg_rest]
}
