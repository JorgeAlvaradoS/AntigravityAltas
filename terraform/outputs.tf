output "cloud_run_service_url" {
  description = "URL pública del portal Seguros Atlas Gastos Médicos Mayores en Cloud Run"
  value       = google_cloud_run_v2_service.seguros_atlas_app.uri
}

output "firestore_database_name" {
  description = "Nombre de la base de datos Cloud Firestore configurada"
  value       = google_firestore_database.default.name
}

output "vertex_ai_search_data_store_id" {
  description = "ID del Data Store de Vertex AI Search (Discovery Engine)"
  value       = google_discovery_engine_data_store.atlas_gmm_ds.data_store_id
}

output "artifact_registry_repository" {
  description = "URL del repositorio Docker en Artifact Registry"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.atlas_repo.repository_id}"
}

output "cloud_run_service_account" {
  description = "Cuenta de servicio asignada a Cloud Run"
  value       = google_service_account.cloud_run_sa.email
}
