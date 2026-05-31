resource "kubernetes_config_map_v1" "sports_portal_html" {
  metadata {
    name      = "sports-portal-html"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }

  data = {
    "index.html" = <<-HTML
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sports Data Platform</title>
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0f1117;
            color: #e2e8f0;
            min-height: 100vh;
            padding: 2rem;
          }
          header {
            max-width: 960px;
            margin: 0 auto 2.5rem;
          }
          header h1 { font-size: 1.8rem; font-weight: 700; color: #f8fafc; }
          header p  { margin-top: 0.4rem; color: #94a3b8; font-size: 0.95rem; }
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 1.25rem;
            max-width: 960px;
            margin: 0 auto;
          }
          .card {
            background: #1e2330;
            border: 1px solid #2d3748;
            border-radius: 10px;
            padding: 1.4rem;
            text-decoration: none;
            color: inherit;
            transition: border-color 0.15s, transform 0.15s;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
          }
          .card:hover { border-color: #4f86f7; transform: translateY(-2px); }
          .card-icon { font-size: 1.6rem; }
          .card-name { font-size: 1rem; font-weight: 600; color: #f1f5f9; }
          .card-desc { font-size: 0.82rem; color: #94a3b8; line-height: 1.4; }
          .section-label {
            max-width: 960px;
            margin: 2.5rem auto 1rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
          }
          .ref-table {
            max-width: 960px;
            margin: 0 auto;
            border-collapse: collapse;
            width: 100%;
            font-size: 0.875rem;
          }
          .ref-table th {
            text-align: left;
            padding: 0.5rem 0.75rem;
            border-bottom: 1px solid #2d3748;
            color: #64748b;
            font-weight: 500;
          }
          .ref-table td {
            padding: 0.55rem 0.75rem;
            border-bottom: 1px solid #1a2030;
            color: #94a3b8;
          }
          .ref-table td:first-child { color: #cbd5e1; font-weight: 500; }
          code {
            font-family: "SFMono-Regular", Consolas, monospace;
            font-size: 0.82rem;
            background: #0d1117;
            padding: 0.1em 0.35em;
            border-radius: 4px;
            color: #7dd3fc;
          }
        </style>
      </head>
      <body>
        <header>
          <h1>Sports Data Platform</h1>
          <p>NFL · MLB · NBA · NHL — medallion architecture on K3s</p>
        </header>

        <div class="section-label">Services</div>
        <div class="grid">
          <a class="card" href="http://airflow.sports.data">
            <span class="card-icon">✈</span>
            <span class="card-name">Airflow</span>
            <span class="card-desc">DAG authoring and pipeline run history</span>
          </a>
          <a class="card" href="http://minio.sports.data">
            <span class="card-icon">🪣</span>
            <span class="card-name">MinIO Console</span>
            <span class="card-desc">Browse and manage bronze S3 buckets</span>
          </a>
          <a class="card" href="http://spark.sports.data">
            <span class="card-icon">⚡</span>
            <span class="card-name">Spark Master</span>
            <span class="card-desc">Active jobs, workers, and executor status</span>
          </a>
          <a class="card" href="http://mlflow.sports.data">
            <span class="card-icon">📈</span>
            <span class="card-name">MLflow</span>
            <span class="card-desc">Experiment tracking and model registry</span>
          </a>
        </div>

        <div class="section-label">API &amp; Database Endpoints</div>
        <table class="ref-table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Endpoint</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>MinIO S3 API</td>
              <td><code>http://192.168.50.231:30900</code></td>
              <td>S3-compatible object storage</td>
            </tr>
            <tr>
              <td>Iceberg REST</td>
              <td><code>http://iceberg.sports.data</code></td>
              <td>/v1/namespaces, /v1/namespaces/{ns}/tables</td>
            </tr>
            <tr>
              <td>PostgreSQL</td>
              <td><code>192.168.50.231:30432</code></td>
              <td>databases: sports_data, airflow, mlflow</td>
            </tr>
          </tbody>
        </table>
      </body>
      </html>
    HTML
  }
}

resource "kubernetes_deployment" "sports_portal" {
  metadata {
    name      = "sports-portal"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
    labels = {
      app = "sports-portal"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "sports-portal"
      }
    }

    template {
      metadata {
        labels = {
          app = "sports-portal"
        }
      }

      spec {
        container {
          name  = "nginx"
          image = "nginx:alpine"

          port {
            container_port = 80
          }

          volume_mount {
            name       = "html"
            mount_path = "/usr/share/nginx/html"
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "32Mi"
            }
            limits = {
              memory = "64Mi"
            }
          }
        }

        volume {
          name = "html"
          config_map {
            name = kubernetes_config_map_v1.sports_portal_html.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "sports_portal" {
  metadata {
    name      = "sports-portal"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }

  spec {
    selector = {
      app = "sports-portal"
    }

    port {
      port        = 80
      target_port = 80
    }

    type = "ClusterIP"
  }
}
