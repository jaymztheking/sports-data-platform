resource "helm_release" "spark" {
  name       = "spark"
  namespace  = kubernetes_namespace.data_platform.metadata[0].name
  repository = "oci://registry-1.docker.io/bitnamicharts"
  chart      = "spark"
  version    = "9.4.1"

  values = [file("${path.module}/../helm-values/spark-values.yaml")]

  set {
    name  = "image.repository"
    value = "${var.image_registry}/spark"
  }

  set {
    name  = "image.tag"
    value = var.spark_image_tag
  }

  set {
    name  = "global.security.allowInsecureImages"
    value = "true"
  }

  depends_on = [helm_release.minio, kubernetes_deployment.iceberg_rest]
}
