locals {
  ghcr_username = split("/", var.image_registry)[1]
}

# imagePullSecret for GHCR private packages.
# Set var.ghcr_token to a PAT with read:packages scope, or make GHCR
# packages public and leave the variable empty (secret still created but unused).
resource "kubernetes_secret" "ghcr_pull_secret" {
  metadata {
    name      = "ghcr-pull-secret"
    namespace = kubernetes_namespace.data_platform.metadata[0].name
  }

  type = "kubernetes.io/dockerconfigjson"

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "ghcr.io" = {
          auth = base64encode("${local.ghcr_username}:${var.ghcr_token}")
        }
      }
    })
  }
}
