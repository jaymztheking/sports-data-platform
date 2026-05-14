resource "kubernetes_deployment" "mlflow" {
  metadata {
    name      = "mlflow"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
    labels = {
      app = "mlflow"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "mlflow"
      }
    }

    template {
      metadata {
        labels = {
          app = "mlflow"
        }
      }

      spec {
        container {
          name  = "mlflow"
          image = "${var.image_registry}/mlflow:${var.mlflow_image_tag}"

          port {
            container_port = 5000
          }

          env {
            name  = "MLFLOW_BACKEND_STORE_URI"
            value = "postgresql://postgres:${var.postgres_password}@postgresql.${kubernetes_namespace.data_platform.metadata[0].name}.svc.cluster.local:5432/mlflow"
          }

          env {
            name  = "MLFLOW_ARTIFACTS_DESTINATION"
            value = "s3://mlflow-artifacts/"
          }

          env {
            name  = "MLFLOW_S3_ENDPOINT_URL"
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

  depends_on = [helm_release.postgresql, helm_release.minio]
}

resource "kubernetes_service" "mlflow" {
  metadata {
    name      = "mlflow"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }

  spec {
    selector = {
      app = "mlflow"
    }

    port {
      port        = 5000
      target_port = 5000
      node_port   = 30500
    }

    type = "NodePort"
  }
}
