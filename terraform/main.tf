terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.30"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.30"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ==============================================================================
# 1. HABILITACIÓN DE APIS EN GCP (ccai-416504)
# ==============================================================================
locals {
  gcp_services = [
    "run.googleapis.com",
    "firestore.googleapis.com",
    "firebase.googleapis.com",
    "aiplatform.googleapis.com",
    "discoveryengine.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com"
  ]
}

resource "google_project_service" "enabled_apis" {
  for_each           = toset(local.gcp_services)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# ==============================================================================
# 2. ARTIFACT REGISTRY PARA IMÁGENES DOCKER
# ==============================================================================
resource "google_artifact_registry_repository" "atlas_repo" {
  location      = var.region
  repository_id = "seguros-atlas-repo"
  description   = "Repositorio de contenedores para el Portal Seguros Atlas Gastos Médicos Mayores"
  format        = "DOCKER"

  depends_on = [google_project_service.enabled_apis]
}

# ==============================================================================
# 3. FIREBASE & CLOUD FIRESTORE (BASE DE DATOS DE COTIZACIONES Y LEADS)
# ==============================================================================
resource "google_firebase_project" "default" {
  provider   = google-beta
  project    = var.project_id
  depends_on = [google_project_service.enabled_apis]
}

resource "google_firestore_database" "default" {
  project                     = var.project_id
  name                        = "(default)"
  location_id                 = var.firestore_location
  type                        = "FIRESTORE_NATIVE"
  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"

  depends_on = [google_firebase_project.default]
}

# Índice compuesto para consultas del Tablero Directivo por Fecha y Plan
resource "google_firestore_index" "quotes_by_date_plan" {
  project    = var.project_id
  database   = google_firestore_database.default.name
  collection = "quotes"

  fields {
    field_path = "dateKey"
    order      = "ASCENDING"
  }

  fields {
    field_path = "planId"
    order      = "ASCENDING"
  }

  fields {
    field_path = "createdAt"
    order      = "DESCENDING"
  }
}

# Índice compuesto para consultas del Tablero Directivo por Plan y Prima Anual
resource "google_firestore_index" "quotes_by_plan_premium" {
  project    = var.project_id
  database   = google_firestore_database.default.name
  collection = "quotes"

  fields {
    field_path = "planId"
    order      = "ASCENDING"
  }

  fields {
    field_path = "annualPremium"
    order      = "DESCENDING"
  }
}

# Reglas de Seguridad de Firestore
resource "google_firebaserules_ruleset" "firestore_rules" {
  provider = google-beta
  project  = var.project_id

  source {
    files {
      name    = "firestore.rules"
      content = file("${path.module}/../firestore.rules")
    }
  }

  depends_on = [google_firestore_database.default]
}

resource "google_firebaserules_release" "firestore_release" {
  provider     = google-beta
  name         = "cloud.firestore"
  ruleset_name = google_firebaserules_ruleset.firestore_rules.name
  project      = var.project_id
}

# ==============================================================================
# 4. VERTEX AI SEARCH (DISCOVERY ENGINE) PARA BUSCADOR INTELIGENTE
# ==============================================================================
resource "google_discovery_engine_data_store" "atlas_gmm_ds" {
  location                    = var.vertex_search_location
  data_store_id               = var.vertex_search_data_store_id
  display_name                = "Seguros Atlas Gastos Médicos Knowledge Base"
  industry_vertical           = "GENERIC"
  content_config              = "CONTENT_REQUIRED"
  solution_types              = ["SOLUTION_TYPE_SEARCH"]
  create_advanced_site_search = false

  depends_on = [google_project_service.enabled_apis]
}

resource "google_discovery_engine_search_engine" "atlas_gmm_engine" {
  engine_id      = "${var.vertex_search_data_store_id}-engine"
  collection_id  = "default_collection"
  location       = google_discovery_engine_data_store.atlas_gmm_ds.location
  display_name   = "Buscador Inteligente Seguros Atlas GMM"
  data_store_ids = [google_discovery_engine_data_store.atlas_gmm_ds.data_store_id]

  search_engine_config {
    search_tier   = "SEARCH_TIER_ENTERPRISE"
    search_add_ons = ["SEARCH_ADD_ON_LLM"]
  }
}

# ==============================================================================
# 5. CUENTA DE SERVICIO E IAM PARA CLOUD RUN
# ==============================================================================
resource "google_service_account" "cloud_run_sa" {
  account_id   = "seguros-atlas-run-sa"
  display_name = "Service Account para Seguros Atlas GMM en Cloud Run"
}

resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "discovery_engine_viewer" {
  project = var.project_id
  role    = "roles/discoveryengine.viewer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# ==============================================================================
# 6. CLOUD RUN V2 SERVICE (PORTAL + API + GEMINI + DASHBOARD)
# ==============================================================================
resource "google_cloud_run_v2_service" "seguros_atlas_app" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    containers {
      image = var.container_image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCP_REGION"
        value = var.region
      }

      env {
        name  = "VERTEX_SEARCH_DATA_STORE_ID"
        value = google_discovery_engine_data_store.atlas_gmm_ds.data_store_id
      }

      env {
        name  = "VERTEX_SEARCH_LOCATION"
        value = var.vertex_search_location
      }

      env {
        name  = "GEMINI_MODEL"
        value = var.gemini_model
      }

      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "true"
      }
    }
  }

  depends_on = [
    google_project_service.enabled_apis,
    google_firestore_database.default,
    google_project_iam_member.firestore_user,
    google_project_iam_member.vertex_ai_user,
    google_project_iam_member.discovery_engine_viewer
  ]
}

# Acceso público HTTPS al portal de Seguros Atlas
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project  = var.project_id
  location = google_cloud_run_v2_service.seguros_atlas_app.location
  name     = google_cloud_run_v2_service.seguros_atlas_app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
