#!/bin/bash

# 🚀 Script de deployment a Google Cloud Run
# Este script despliega BioLaySumm en Google Cloud Run

set -e  # Detener si hay error

echo "🚀 BioLaySumm - Deployment a Google Cloud Run"
echo "=============================================="
echo ""

# ========================================
# CONFIGURACIÓN - EDITA ESTOS VALORES
# ========================================

PROJECT_ID="tu-proyecto-gcp"           # Tu ID de proyecto en GCP
REGION="us-central1"                    # Región de Cloud Run
SERVICE_NAME_PREFIX="biolaysum"         # Prefijo para los servicios

# URLs de los servicios (se generan después del primer deploy)
# Déjalas vacías en el primer deploy
API_SUMMARY_URL=""
API_METRICS_URL=""

# Token de Hugging Face (opcional pero recomendado)
HF_TOKEN=""

# ========================================
# FIN DE CONFIGURACIÓN
# ========================================

echo "📋 Configuración:"
echo "  Proyecto GCP: $PROJECT_ID"
echo "  Región: $REGION"
echo "  Prefijo de servicios: $SERVICE_NAME_PREFIX"
echo ""

# Verificar que gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI no está instalado"
    echo "   Instálalo desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Configurar proyecto
echo "🔧 Configurando proyecto GCP..."
gcloud config set project $PROJECT_ID

# Habilitar APIs necesarias
echo "🔧 Habilitando APIs necesarias..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo ""
echo "=============================================="
echo "📦 PASO 1: Construir y subir API de Métricas"
echo "=============================================="
echo ""

# Construir y subir API Metrics
SERVICE_METRICS="${SERVICE_NAME_PREFIX}-api-metrics"
IMAGE_METRICS="gcr.io/${PROJECT_ID}/${SERVICE_METRICS}:latest"

echo "🏗️  Construyendo imagen de métricas..."

# Copiar Dockerfile temporal
cp Dockerfile.metrics.cloudrun Dockerfile

# Build
gcloud builds submit --tag ${IMAGE_METRICS} .

# Limpiar
rm -f Dockerfile

echo "🚀 Desplegando servicio de métricas..."
gcloud run deploy ${SERVICE_METRICS} \
    --image ${IMAGE_METRICS} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10

# Obtener URL del servicio de métricas
API_METRICS_URL=$(gcloud run services describe ${SERVICE_METRICS} --region ${REGION} --format 'value(status.url)')
echo "✅ API Metrics desplegada en: ${API_METRICS_URL}"

echo ""
echo "=============================================="
echo "📦 PASO 2: Construir y subir API de Resumen"
echo "=============================================="
echo ""

# Construir y subir API Summary
SERVICE_SUMMARY="${SERVICE_NAME_PREFIX}-api-summary"
IMAGE_SUMMARY="gcr.io/${PROJECT_ID}/${SERVICE_SUMMARY}:latest"

echo "🏗️  Construyendo imagen de resumen..."

# Copiar Dockerfile temporal
cp Dockerfile.summary.cloudrun Dockerfile

# Build
gcloud builds submit --tag ${IMAGE_SUMMARY} .

# Limpiar
rm -f Dockerfile

echo "🚀 Desplegando servicio de resumen..."
gcloud run deploy ${SERVICE_SUMMARY} \
    --image ${IMAGE_SUMMARY} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 8Gi \
    --cpu 4 \
    --timeout 600 \
    --max-instances 5

# Obtener URL del servicio de resumen
API_SUMMARY_URL=$(gcloud run services describe ${SERVICE_SUMMARY} --region ${REGION} --format 'value(status.url)')
echo "✅ API Summary desplegada en: ${API_SUMMARY_URL}"

echo ""
echo "=============================================="
echo "📦 PASO 3: Construir y subir Streamlit"
echo "=============================================="
echo ""

# Construir y subir Streamlit
SERVICE_STREAMLIT="${SERVICE_NAME_PREFIX}-streamlit"
IMAGE_STREAMLIT="gcr.io/${PROJECT_ID}/${SERVICE_STREAMLIT}:latest"

echo "🏗️  Construyendo imagen de Streamlit..."

# Copiar Dockerfile temporal
cp Dockerfile.streamlit.cloudrun Dockerfile

# Build
gcloud builds submit --tag ${IMAGE_STREAMLIT} .

# Limpiar
rm -f Dockerfile

echo "🚀 Desplegando servicio de Streamlit..."
gcloud run deploy ${SERVICE_STREAMLIT} \
    --image ${IMAGE_STREAMLIT} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars "API_CLASSIFY_URL=${API_SUMMARY_URL}/process,API_SUMMARY_URL=${API_SUMMARY_URL}/summary,API_METRICS_URL=${API_METRICS_URL}/metrics"

# Obtener URL del servicio de Streamlit
STREAMLIT_URL=$(gcloud run services describe ${SERVICE_STREAMLIT} --region ${REGION} --format 'value(status.url)')

echo ""
echo "=============================================="
echo "✅ DEPLOYMENT COMPLETADO"
echo "=============================================="
echo ""
echo "🌐 URLs de los servicios:"
echo "  Streamlit:    ${STREAMLIT_URL}"
echo "  API Summary:  ${API_SUMMARY_URL}"
echo "  API Metrics:  ${API_METRICS_URL}"
echo ""
echo "🎉 ¡Tu aplicación está lista!"
echo "   Abre: ${STREAMLIT_URL}"
echo ""
echo "💡 Para actualizar los servicios en el futuro:"
echo "   ./deploy-cloudrun.sh"
echo ""