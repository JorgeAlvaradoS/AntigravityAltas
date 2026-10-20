# Seguros Atlas — Portal Digital de Seguros de Gastos Médicos Mayores (AI-First)

Plataforma integral modernizada para **Seguros Atlas — Seguros de Gastos Médicos Mayores**, diseñada para maximizar la atracción de clientes, generación de leads calificados y visibilidad ejecutiva en tiempo real sobre **Google Cloud Platform (`ccai-416504`)**.

---

## Arquitectura y Alcance (Pasos 1 al 8)

1. **Clonación del Catálogo Oficial de Seguros Atlas (Paso 1)**:
   - Réplica completa del catálogo de [Seguros de Gastos Médicos](https://www.segurosatlas.com.mx/seguros-de-gastos-medicos.html) y sus vistas de detalle para:
     - **Med Óptimo** (Individual/Familiar, hasta 1,250 UMAs)
     - **Med Plus** (Flexibilidad de niveles hospitalarios y tabuladores médicos)
     - **Med Plus Elite** (Cero deducible por accidente, 100% honorarios médicos, cobertura nacional e internacional)
     - **Plan Mundial** (Hasta $2,000,000 USD con red internacional Global Medical Management)
     - **Planes Colectivos / Empresariales** (*Med Óptimo para Empresas*, *Med Plus para Empresas*) y *Básicos Estandarizados*.
   - Guía interactiva oficial de **[En Caso de Siniestro](https://www.segurosatlas.com.mx/en-caso-de-siniestro.html)** (Pago Directo vs. Reembolso, CITAMED `55 9177 5144` / `800 849 3918`, Med Asistencia `55 5254 7086` y Global Medical `+1 954 308-3932`).

2. **Modernización UX/UI Orientada a Conversión (Paso 2)**:
   - Identidad visual de Seguros Atlas (`#508CBE` Azul Médico, `#FAA632` Naranja Atlas, `#6F6259` Gris Cálido, `#D9272E` Rojo Atlas).
   - Comparador interactivo lado a lado, modales de detalle con folletos y condiciones generales oficiales, micro-interacciones y accesibilidad.

3. **Buscador Inteligente con Vertex AI Search (Paso 3)**:
   - Integración con **Google Cloud Discovery Engine (Vertex AI Search)** + síntesis generativa con **Gemini** fundamentada en condiciones generales, coberturas y protocolos de siniestro.

4. **Agente Conversacional con Gemini (`Atlas Med AI`) (Paso 4)**:
   - Impulsado por el SDK oficial `google-genai` (`gemini-3.8-flash` / `gemini-2.5-flash`).
   - Resuelve dudas sobre planes, guía paso a paso en **Caso de Siniestro**, cotiza en tiempo real dentro del chat y asigna un Agente Certificado CNSF.

5. **Cotizador Rápido Actuarial + Tablero Directivo BI (Paso 5)**:
   - Motor de cálculo basado en reglas actuariales estándar del mercado mexicano de SGMM (edad, género, dependientes, plan, deducible, coaseguro y coberturas adicionales de Dental, Visión y Emergencia en el Extranjero).
   - Asignación automática de un **Agente Profesional Certificado de Seguros Atlas** y persistencia en **Cloud Firestore**.
   - **Tablero Directivo (Executive Dashboard)** con gráficas de cotizaciones y potencial de negocio por día (`YYYY-MM-DD`), mezcla por tipo de plan, desempeño por agente y bitácora consolidada.

6. **Repositorio GitHub (Paso 6)**:
   - Código fuente versionado para [`https://github.com/JorgeAlvaradoS/AntigravityAltas.git`](https://github.com/JorgeAlvaradoS/AntigravityAltas.git).

7. **Despliegue en GCP con Cloud Run y Firebase/Firestore (Paso 7)**:
   - Configurado para el proyecto `ccai-416504` usando **Cloud Run** y **Cloud Firestore** (`firestore.rules`, `firestore.indexes.json`, `firebase.json`).

8. **Infraestructura como Código con Terraform (Paso 8)**:
   - Directorio [`terraform/`](./terraform) con aprovisionamiento declarativo de APIs, Artifact Registry, Firebase/Firestore, índices compuestos, reglas de seguridad, Vertex AI Search Data Store + Engine y Cloud Run v2.

---

## Ejecución Local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

Abrir en el navegador: `http://localhost:8080`

---

## Despliegue en Google Cloud (`ccai-416504`)

### Opción A: Despliegue Directo con `gcloud` CLI
```bash
gcloud auth login
gcloud config set project ccai-416504

# Crear base de datos Firestore (si aún no existe en el proyecto)
gcloud firestore databases create --location=nam5 --project=ccai-416504

# Desplegar servicio en Cloud Run desde código fuente
gcloud run deploy seguros-atlas-gmm \
  --source . \
  --project ccai-416504 \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=ccai-416504,GCP_REGION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=true,VERTEX_SEARCH_DATA_STORE_ID=seguros-atlas-gmm-ds"
```

### Opción B: Aprovisionamiento con Terraform
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```
