@echo off
echo 🐳 BioLaySumm - Docker Setup
echo ==============================
echo.

REM Verificar que Docker está corriendo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker no está corriendo
    echo    Por favor inicia Docker Desktop primero
    pause
    exit /b 1
)

echo ✅ Docker está corriendo
echo.

REM Verificar modelos
echo 🔍 Verificando modelos...

if not exist "src\models\deepseek-coder-1p3b-lora-base" (
    echo ⚠️  Advertencia: Modelo base no encontrado
)

if not exist "src\models\alignscore\AlignScore-large.ckpt" (
    echo ⚠️  Advertencia: AlignScore no encontrado
)

if not exist "outputs\deepseek-coder-1p3b-qlora\checkpoint-191" (
    echo ⚠️  Advertencia: Checkpoint LoRA no encontrado
)

echo.
echo 🏗️  Construyendo imágenes Docker...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Error al construir las imágenes
    pause
    exit /b 1
)

echo.
echo 🚀 Levantando servicios...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Error al levantar los servicios
    pause
    exit /b 1
)

echo.
echo ⏳ Esperando a que los servicios estén listos...
timeout /t 5 /nobreak >nul

echo.
echo 📊 Estado de los servicios:
docker-compose ps

echo.
echo ✅ ¡Listo! Servicios disponibles en:
echo.
echo    🌐 Streamlit UI:     http://localhost:8501
echo    📡 API Summary:      http://localhost:8000/docs
echo    📊 API Metrics:      http://localhost:8001/docs
echo.
echo 💡 Comandos útiles:
echo    Ver logs:            docker-compose logs -f
echo    Detener:             docker-compose down
echo    Reiniciar:           docker-compose restart
echo.
pause