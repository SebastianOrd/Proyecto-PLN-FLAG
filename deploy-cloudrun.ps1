# 🚀 BioLaySumm - Deploy to Google Cloud Run
# PowerShell Script

# ========================================
# CONFIGURACIÓN
# ========================================
$PROJECT_ID = "proyecto-pln-flag"
$REGION = "us-central1"
$SERVICE_NAME_PREFIX = "biolaysum"

# ========================================

Write-Host "🚀 BioLaySumm - Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Config:"
Write-Host "  Project: $PROJECT_ID"
Write-Host "  Region: $REGION"
Write-Host ""

# Set project
gcloud config set project $PROJECT_ID

# Enable APIs
Write-Host "🔧 Enabling APIs..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com
Write-Host ""

# ========================================
# PASO 1: API METRICS
# ========================================
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "📦 PASO 1: API Metrics" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

$SERVICE_METRICS = "$SERVICE_NAME_PREFIX-api-metrics"
$IMAGE_METRICS = "gcr.io/${PROJECT_ID}/${SERVICE_METRICS}:latest"

Write-Host "Building: $IMAGE_METRICS" -ForegroundColor Green

# Copy and build
Copy-Item "Dockerfile.metrics.cloudrun" "Dockerfile" -Force
gcloud builds submit --tag $IMAGE_METRICS .
$BUILD_EXIT = $LASTEXITCODE
Remove-Item "Dockerfile" -ErrorAction SilentlyContinue

if ($BUILD_EXIT -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Deploying..." -ForegroundColor Green
gcloud run deploy $SERVICE_METRICS --image $IMAGE_METRICS --platform managed --region $REGION --allow-unauthenticated --memory 4Gi --cpu 2 --timeout 300 --max-instances 10

$API_METRICS_URL = gcloud run services describe $SERVICE_METRICS --region $REGION --format 'value(status.url)'
Write-Host "✅ Deployed: $API_METRICS_URL" -ForegroundColor Green
Write-Host ""

# ========================================
# PASO 2: API SUMMARY
# ========================================
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "📦 PASO 2: API Summary" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

$SERVICE_SUMMARY = "$SERVICE_NAME_PREFIX-api-summary"
$IMAGE_SUMMARY = "gcr.io/${PROJECT_ID}/${SERVICE_SUMMARY}:latest"

Write-Host "Building: $IMAGE_SUMMARY" -ForegroundColor Green

# Copy and build
Copy-Item "Dockerfile.summary.cloudrun" "Dockerfile" -Force
gcloud builds submit --tag $IMAGE_SUMMARY .
$BUILD_EXIT = $LASTEXITCODE
Remove-Item "Dockerfile" -ErrorAction SilentlyContinue

if ($BUILD_EXIT -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Deploying..." -ForegroundColor Green
gcloud run deploy $SERVICE_SUMMARY --image $IMAGE_SUMMARY --platform managed --region $REGION --allow-unauthenticated --memory 8Gi --cpu 4 --timeout 600 --max-instances 5

$API_SUMMARY_URL = gcloud run services describe $SERVICE_SUMMARY --region $REGION --format 'value(status.url)'
Write-Host "✅ Deployed: $API_SUMMARY_URL" -ForegroundColor Green
Write-Host ""

# ========================================
# PASO 3: STREAMLIT
# ========================================
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "📦 PASO 3: Streamlit" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

$SERVICE_STREAMLIT = "$SERVICE_NAME_PREFIX-streamlit"
$IMAGE_STREAMLIT = "gcr.io/${PROJECT_ID}/${SERVICE_STREAMLIT}:latest"

Write-Host "Building: $IMAGE_STREAMLIT" -ForegroundColor Green

# Copy and build
Copy-Item "Dockerfile.streamlit.cloudrun" "Dockerfile" -Force
gcloud builds submit --tag $IMAGE_STREAMLIT .
$BUILD_EXIT = $LASTEXITCODE
Remove-Item "Dockerfile" -ErrorAction SilentlyContinue

if ($BUILD_EXIT -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Deploying..." -ForegroundColor Green
$ENV_VARS = "API_CLASSIFY_URL=${API_SUMMARY_URL}/process,API_SUMMARY_URL=${API_SUMMARY_URL}/summary,API_METRICS_URL=${API_METRICS_URL}/metrics"
gcloud run deploy $SERVICE_STREAMLIT --image $IMAGE_STREAMLIT --platform managed --region $REGION --allow-unauthenticated --memory 2Gi --cpu 1 --timeout 300 --max-instances 10 --set-env-vars $ENV_VARS

$STREAMLIT_URL = gcloud run services describe $SERVICE_STREAMLIT --region $REGION --format 'value(status.url)'
Write-Host "✅ Deployed: $STREAMLIT_URL" -ForegroundColor Green
Write-Host ""

# ========================================
# RESUMEN
# ========================================
Write-Host "==============================================" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URLs:" -ForegroundColor Yellow
Write-Host "  Streamlit:   $STREAMLIT_URL"
Write-Host "  API Summary: $API_SUMMARY_URL"
Write-Host "  API Metrics: $API_METRICS_URL"
Write-Host ""
Write-Host "🎉 App ready at: $STREAMLIT_URL" -ForegroundColor Cyan
Write-Host ""