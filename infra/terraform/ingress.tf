locals {
  ingress_annotations = {
    "kubernetes.io/ingress.class" = "traefik"
  }
}

resource "kubernetes_ingress_v1" "sports_portal" {
  metadata {
    name        = "sports-portal"
    namespace   = kubernetes_namespace.data_platform.metadata[0].name
    annotations = local.ingress_annotations
  }

  spec {
    ingress_class_name = "traefik"

    rule {
      host = "sports.data"
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.sports_portal.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_ingress_v1" "airflow" {
  metadata {
    name        = "airflow"
    namespace   = kubernetes_namespace.data_platform.metadata[0].name
    annotations = local.ingress_annotations
  }

  spec {
    ingress_class_name = "traefik"

    rule {
      host = "airflow.sports.data"
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = "airflow-webserver"
              port {
                number = 8080
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_ingress_v1" "minio" {
  metadata {
    name        = "minio"
    namespace   = kubernetes_namespace.data_platform.metadata[0].name
    annotations = local.ingress_annotations
  }

  spec {
    ingress_class_name = "traefik"

    rule {
      host = "minio.sports.data"
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = "minio-console"
              port {
                number = 9001
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_ingress_v1" "spark" {
  metadata {
    name        = "spark"
    namespace   = kubernetes_namespace.data_platform.metadata[0].name
    annotations = local.ingress_annotations
  }

  spec {
    ingress_class_name = "traefik"

    rule {
      host = "spark.sports.data"
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.spark_master_svc.metadata[0].name
              port {
                number = 8080
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_ingress_v1" "mlflow" {
  metadata {
    name        = "mlflow"
    namespace   = kubernetes_namespace.data_platform.metadata[0].name
    annotations = local.ingress_annotations
  }

  spec {
    ingress_class_name = "traefik"

    rule {
      host = "mlflow.sports.data"
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.mlflow.metadata[0].name
              port {
                number = 5000
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_ingress_v1" "iceberg" {
  metadata {
    name        = "iceberg"
    namespace   = kubernetes_namespace.data_platform.metadata[0].name
    annotations = local.ingress_annotations
  }

  spec {
    ingress_class_name = "traefik"

    rule {
      host = "iceberg.sports.data"
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.iceberg_rest.metadata[0].name
              port {
                number = 8181
              }
            }
          }
        }
      }
    }
  }
}
