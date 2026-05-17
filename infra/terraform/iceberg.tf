resource "kubernetes_deployment" "iceberg_rest" {
  metadata {
    name      = "iceberg-rest"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
    labels = {
      app = "iceberg-rest"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "iceberg-rest"
      }
    }

    template {
      metadata {
        labels = {
          app = "iceberg-rest"
        }
      }

      spec {
        container {
          name  = "iceberg-rest"
          image = "tabulario/iceberg-rest:1.5.0"

          port {
            container_port = 8181
          }

          env {
            name  = "CATALOG_WAREHOUSE"
            value = "s3://spark-warehouse/"
          }

          env {
            name  = "CATALOG_IO__IMPL"
            value = "org.apache.iceberg.aws.s3.S3FileIO"
          }

          env {
            name  = "CATALOG_S3_ENDPOINT"
            value = "http://minio.${kubernetes_namespace.data_platform.metadata[0].name}.svc.cluster.local:9000"
          }

          env {
            name  = "AWS_ACCESS_KEY_ID"
            value = "minioadmin"
          }

          env {
            name  = "AWS_SECRET_ACCESS_KEY"
            value_from {
              secret_key_ref {
                name = "minio"
                key  = "rootPassword"
              }
            }
          }

          env {
            name  = "AWS_REGION"
            value = "us-east-1"
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
            limits = {
              memory = "512Mi"
            }
          }
        }
      }
    }
  }

  depends_on = [helm_release.minio]
}

resource "kubernetes_service" "iceberg_rest" {
  metadata {
    name      = "iceberg-rest"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }

  spec {
    selector = {
      app = "iceberg-rest"
    }

    port {
      port        = 8181
      target_port = 8181
      node_port   = 30181
    }

    type = "NodePort"
  }
}
