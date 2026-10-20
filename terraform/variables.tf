variable "project_id" {
  description = "ID del proyecto de Google Cloud Platform donde se desplegará Seguros Atlas GMM"
  type        = string
  default     = "ccai-416504"
}

variable "region" {
  description = "Región de Google Cloud para Cloud Run y Artifact Registry"
  type        = string
  default     = "us-central1"
}

variable "firestore_location" {
  description = "Ubicación de la base de datos de Cloud Firestore (nam5 = multi-región US o us-central1)"
  type        = string
  default     = "nam5"
}

variable "service_name" {
  description = "Nombre del servicio en Cloud Run"
  type        = string
  default     = "seguros-atlas-gmm"
}

variable "container_image" {
  description = "Imagen de contenedor para Cloud Run (Artifact Registry / GCR)"
  type        = string
  default     = "us-central1-docker.pkg.dev/ccai-416504/seguros-atlas-repo/seguros-atlas-gmm:latest"
}

variable "vertex_search_location" {
  description = "Ubicación para Vertex AI Search (Discovery Engine)"
  type        = string
  default     = "global"
}

variable "vertex_search_data_store_id" {
  description = "Identificador del Data Store de Vertex AI Search para pólizas y guías de Seguros Atlas"
  type        = string
  default     = "seguros-atlas-gmm-ds"
}

variable "gemini_model" {
  description = "Modelo de Google Gemini utilizado para el agente conversacional y síntesis de búsqueda"
  type        = string
  default     = "gemini-3.8-flash"
}
