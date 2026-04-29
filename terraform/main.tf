provider "google" {
  project = var.project_id
  region  = var.app_region
}

# 必要なAPIの有効化
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "compute.googleapis.com",
    "iam.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "firestore.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# Firestore database for persistent ADK sessions
resource "google_firestore_database" "default" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.firestore_location_id
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.services]
}

# Artifact Registry リポジトリ
resource "google_artifact_registry_repository" "repo" {
  location      = var.app_region
  repository_id = "madamis-ai"
  description   = "Docker images for madamis-ai"
  format        = "DOCKER"
  depends_on    = [google_project_service.services]
}

# --- Secret Manager ---
# Google API Key
resource "google_secret_manager_secret" "google_api_key" {
  secret_id = "google-api-key"
  replication {
    auto {}
  }

  depends_on = [google_project_service.services]
}

resource "google_secret_manager_secret_version" "google_api_key" {
  secret      = google_secret_manager_secret.google_api_key.id
  secret_data = var.google_api_key
}

# Discord Bot Token
resource "google_secret_manager_secret" "discord_bot_token" {
  secret_id = "discord-bot-token"
  replication {
    auto {}
  }

  depends_on = [google_project_service.services]
}

resource "google_secret_manager_secret_version" "discord_bot_token" {
  secret      = google_secret_manager_secret.discord_bot_token.id
  secret_data = var.discord_bot_token
}

# --- Service Account for Cloud Run & GCE ---
resource "google_service_account" "app_sa" {
  account_id   = "madamis-ai-sa"
  display_name = "madamis-ai application"
}

# 権限付与: Artifact Registry からイメージを取得
resource "google_project_iam_member" "artifact_registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# 権限付与: Secret Manager の読み取り
resource "google_secret_manager_secret_iam_member" "api_key_accessor" {
  secret_id = google_secret_manager_secret.google_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "bot_token_accessor" {
  secret_id = google_secret_manager_secret.discord_bot_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app_sa.email}"
}

# 権限付与: Firestore の読み書き
resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}

# --- Cloud Run (Backend) ---
resource "google_cloud_run_v2_service" "backend" {
  name     = "madamis-backend"
  location = var.app_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  template {
    service_account = google_service_account.app_sa.email
    containers {
      image = "${var.app_region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.name}/backend:${var.backend_image_tag}"
      ports {
        container_port = 8000
      }
      env {
        name = "GOOGLE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.google_api_key.secret_id
            version = "latest"
          }
        }
      }
      env {
        name  = "ADK_SESSION_SERVICE"
        value = "firestore"
      }
      env {
        name  = "FIRESTORE_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "FIRESTORE_DATABASE_ID"
        value = google_firestore_database.default.name
      }
      env {
        name  = "ADK_FIRESTORE_ROOT_COLLECTION"
        value = "adk-session"
      }
    }
  }
  depends_on = [
    google_firestore_database.default,
    google_project_iam_member.firestore_user,
    google_secret_manager_secret_iam_member.api_key_accessor
  ]
}

# 誰でもアクセス可能にする
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  location = google_cloud_run_v2_service.backend.location
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# --- Cloud Run (Frontend) ---
resource "google_cloud_run_v2_service" "frontend" {
  name     = "madamis-frontend"
  location = var.app_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }

  template {
    service_account = google_service_account.app_sa.email
    containers {
      image = "${var.app_region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.name}/frontend:${var.frontend_image_tag}"
      ports {
        container_port = 3000
      }
      env {
        name  = "NEXT_PUBLIC_BACKEND_URL"
        value = google_cloud_run_v2_service.backend.uri
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  location = google_cloud_run_v2_service.frontend.location
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# --- Compute Engine (Discord Bot Interface) ---
resource "google_compute_instance" "interface" {
  name         = "madamis-interface"
  machine_type = "e2-micro"
  zone         = var.gce_zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 10
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io jq
    
    # Artifact Registry 認証
    gcloud auth configure-docker ${var.app_region}-docker.pkg.dev --quiet

    # Secret Manager から最新のトークンを取得
    DISCORD_BOT_TOKEN=$(gcloud secrets versions access latest --secret="${google_secret_manager_secret.discord_bot_token.secret_id}")

    docker run -d \
      --name interface \
      --restart always \
      -e DISCORD_BOT_TOKEN="$DISCORD_BOT_TOKEN" \
      -e API_BASE_URL="${google_cloud_run_v2_service.backend.uri}" \
      ${var.app_region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.name}/interface:${var.interface_image_tag}
  EOT

  service_account {
    email  = google_service_account.app_sa.email
    scopes = ["cloud-platform"]
  }
  depends_on = [google_secret_manager_secret_iam_member.bot_token_accessor]
}

output "backend_url" {
  value = google_cloud_run_v2_service.backend.uri
}

output "frontend_url" {
  value = google_cloud_run_v2_service.frontend.uri
}
