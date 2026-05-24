locals {
  spark_image = "${var.image_registry}/spark:${var.spark_image_tag}"
  spark_master_labels = {
    app       = "spark"
    component = "master"
  }
  spark_worker_labels = {
    app       = "spark"
    component = "worker"
  }
}

resource "kubernetes_service" "spark_master_svc" {
  metadata {
    name      = "spark-master-svc"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }
  spec {
    selector = local.spark_master_labels
    type     = "NodePort"
    port {
      name        = "cluster"
      port        = 7077
      target_port = 7077
      protocol    = "TCP"
    }
    port {
      name        = "http"
      port        = 8080
      target_port = 8080
      node_port   = 30808
      protocol    = "TCP"
    }
  }
}

resource "kubernetes_stateful_set" "spark_master" {
  metadata {
    name      = "spark-master"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }
  spec {
    service_name = kubernetes_service.spark_master_svc.metadata[0].name
    replicas     = 1

    selector {
      match_labels = local.spark_master_labels
    }

    template {
      metadata {
        labels = local.spark_master_labels
      }
      spec {
        image_pull_secrets {
          name = kubernetes_secret.ghcr_pull_secret.metadata[0].name
        }

        security_context {
          run_as_user     = 185
          run_as_non_root = true
          fs_group        = 185
        }

        container {
          name              = "spark-master"
          image             = local.spark_image
          image_pull_policy = "Always"

          env {
            name  = "SPARK_MODE"
            value = "master"
          }
          env {
            name  = "SPARK_MASTER_PORT"
            value = "7077"
          }
          env {
            name  = "SPARK_MASTER_WEBUI_PORT"
            value = "8080"
          }

          port {
            name           = "cluster"
            container_port = 7077
          }
          port {
            name           = "http"
            container_port = 8080
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "512Mi"
            }
            limits = {
              memory = "1Gi"
            }
          }

          liveness_probe {
            tcp_socket {
              port = "8080"
            }
            initial_delay_seconds = 60
            period_seconds        = 20
            failure_threshold     = 6
          }

          readiness_probe {
            http_get {
              path = "/"
              port = 8080
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            failure_threshold     = 6
          }
        }
      }
    }
  }

  depends_on = [helm_release.minio, kubernetes_deployment.iceberg_rest]
}

resource "kubernetes_service" "spark_worker_headless" {
  metadata {
    name      = "spark-worker-headless"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }
  spec {
    cluster_ip = "None"
    selector   = local.spark_worker_labels
    port {
      name = "http"
      port = 8081
    }
  }
}

resource "kubernetes_stateful_set" "spark_worker" {
  metadata {
    name      = "spark-worker"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }
  spec {
    service_name = kubernetes_service.spark_worker_headless.metadata[0].name
    replicas     = 2

    selector {
      match_labels = local.spark_worker_labels
    }

    template {
      metadata {
        labels = local.spark_worker_labels
      }
      spec {
        image_pull_secrets {
          name = kubernetes_secret.ghcr_pull_secret.metadata[0].name
        }

        security_context {
          run_as_user     = 185
          run_as_non_root = true
          fs_group        = 185
        }

        container {
          name              = "spark-worker"
          image             = local.spark_image
          image_pull_policy = "Always"

          env {
            name  = "SPARK_MODE"
            value = "worker"
          }
          env {
            name  = "SPARK_MASTER_URL"
            value = "spark://spark-master-svc:7077"
          }
          env {
            name  = "SPARK_WORKER_WEBUI_PORT"
            value = "8081"
          }

          port {
            name           = "http"
            container_port = 8081
          }

          resources {
            requests = {
              cpu    = "200m"
              memory = "512Mi"
            }
            limits = {
              memory = "1Gi"
            }
          }

          liveness_probe {
            tcp_socket {
              port = "8081"
            }
            initial_delay_seconds = 60
            period_seconds        = 20
            failure_threshold     = 6
          }

          readiness_probe {
            http_get {
              path = "/"
              port = 8081
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            failure_threshold     = 6
          }
        }
      }
    }
  }

  depends_on = [kubernetes_stateful_set.spark_master]
}
