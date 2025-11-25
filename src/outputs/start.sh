#!/bin/bash

echo "🐳 BioLaySumm - Docker Setup"
echo "=============================="
echo ""

# Verificar que Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo"
    echo "   Por favor inicia Docker Desktop primero"
    exit 1
fi

echo "✅ Docker está corriendo"
echo ""

# Verificar archivos de modelos
echo "🔍 Verificando modelos..."

if [ ! -d "src/models/deepseek-coder-1p3b-lora-base" ]; then
    echo "⚠️  Advertencia: Modelo base no encontrado en src/models/deepseek-coder-1p3b-lora-base/"
fi

if [ ! -f "src/models/alignscore/AlignScore-large.ckpt" ]; then
    echo "⚠️  Advertencia: AlignScore no encontrado en src/models/alignscore/"
fi

if [ ! -d "outputs/deepseek-coder-1p3b-qlora/checkpoint-191" ]; then
    echo "⚠️  Advertencia: Checkpoint LoRA no encontrado en outputs/"
fi

echo ""
echo "🏗️  Construyendo imágenes Docker..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Error al construir las imágenes"
    exit 1
fi

echo ""
echo "🚀 Levantando servicios..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Error al levantar los servicios"
    exit 1
fi

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 5

echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

echo ""
echo "✅ ¡Listo! Servicios disponibles en:"
echo ""
echo "   🌐 Streamlit UI:     http://localhost:8501"
echo "   📡 API Summary:      http://localhost:8000/docs"
echo "   📊 API Metrics:      http://localhost:8001/docs"
echo ""
echo "💡 Comandos útiles:"
echo "   Ver logs:            docker-compose logs -f"
echo "   Detener:             docker-compose down"
echo "   Reiniciar:           docker-compose restart"
echo ""