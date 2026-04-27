variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region (use us-central1, us-east1, or us-west1 for GCE Free Tier)"
  type        = string
  default     = "us-central1"
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
