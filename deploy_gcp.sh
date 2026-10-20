#!/usr/bin/env zsh
set -e

GCLOUD="/Users/jorgealvarados/google-cloud-sdk/bin/gcloud"
GIT="/usr/local/git/current/bin/git"
PROJECT_ID="ccai-416504"
REGION="us-central1"
SERVICE_NAME="seguros-atlas-gmm"

echo "=================================================================="
echo " Seguros Atlas — Despliegue en GCP (ccai-416504) y GitHub"
echo "=================================================================="

echo "\n[1/5] Verificando autenticación en Google Cloud..."
if ! "$GCLOUD" projects describe "$PROJECT_ID" --quiet >/dev/null 2>&1; then
  echo "Iniciando autenticación interactiva en navegador con Google Cloud..."
  "$GCLOUD" auth login
  "$GCLOUD" auth application-default login
fi

"$GCLOUD" config set project "$PROJECT_ID"

echo "\n[2/5] Habilitando APIs de Cloud Run, Firestore, Vertex AI y Discovery Engine..."
"$GCLOUD" services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  firebase.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  --project="$PROJECT_ID"

echo "\n[3/5] Verificando / Creando base de datos Cloud Firestore en $PROJECT_ID..."
if ! "$GCLOUD" firestore databases describe --database="(default)" --project="$PROJECT_ID" >/dev/null 2>&1; then
  "$GCLOUD" firestore databases create --location=nam5 --database="(default)" --project="$PROJECT_ID" || true
else
  echo "Base de datos Firestore (default) ya activa en $PROJECT_ID."
fi

echo "\n[4/5] Desplegando Portal Seguros Atlas GMM en Cloud Run ($PROJECT_ID / $REGION)..."
"$GCLOUD" run deploy "$SERVICE_NAME" \
  --source . \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,GCP_REGION=$REGION,GOOGLE_GENAI_USE_VERTEXAI=true,VERTEX_SEARCH_ENGINE_ID=seguros-atlas-gmm-search"

echo "\n[5/5] Subiendo código a GitHub (https://github.com/JorgeAlvaradoS/AntigravityAltas.git)..."
"$GIT" push -u origin main --force

echo "\n=================================================================="
echo " ¡Despliegue completado con éxito!"
echo "=================================================================="
