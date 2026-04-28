variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "app_region" {
  description = "GCP region for Cloud Run and Artifact Registry."
  type        = string
  default     = "asia-northeast1"
}

variable "gce_zone" {
  description = "GCE zone for the Discord bot. Use a Free Tier eligible zone such as us-west1-a, us-central1-a, or us-east1-b."
  type        = string
  default     = "us-west1-a"
}

variable "firestore_location_id" {
  description = "Firestore database location. This is immutable after creation."
  type        = string
  default     = "asia-northeast1"
}

variable "discord_bot_token" {
  description = "Discord Bot Token (Sensitive)"
  type        = string
  sensitive   = true
}

variable "google_api_key" {
  description = "Google Generative AI API Key (Sensitive)"
  type        = string
  sensitive   = true
}
