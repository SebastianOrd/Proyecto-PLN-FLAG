# src/api/summary/model_loader.py
import torch
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from google.cloud import storage

# Descargar modelos desde GCS si no existen
def download_from_gcs_if_needed():
    bucket_name = "proyecto-pln-flag-models"
    local_base_dir = "/app/modelos"
    
    # Crear directorios
    os.makedirs(f"{local_base_dir}/deepseek-coder-1p3b-merged", exist_ok=True)

    
    # Si ya existen, skip
    if os.path.exists(f"{local_base_dir}/deepseek-coder-1p3b-merged/config.json"):
        print("✅ Modelo ya descargado")
        return local_base_dir
    
    print("📥 Descargando modelos desde GCS...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Descargar modelo 
    blobs = bucket.list_blobs(prefix="deepseek-coder-1p3b-lora-merged/")
    for blob in blobs:
        if not blob.name.endswith("/"):
            local_path = f"{local_base_dir}/{blob.name}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            blob.download_to_filename(local_path)
            print(f"  ✓ {blob.name}")
    
    print("✅ Modelo descargado")
    return local_base_dir

# Descargar modelos
BASE_DIR = download_from_gcs_if_needed()

MODEL_DIR = f"{BASE_DIR}/deepseek-coder-1p3b-merged"

print(f"🔍 Cargando tokenizer desde: {MODEL_DIR}")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR,
    use_fast=True,
    trust_remote_code=True,
    local_files_only=True
)

print(f"🔍 Cargando modelo base...")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    device_map="cpu",
    trust_remote_code=True,
    local_files_only=True
)
model.eval()
model.config.use_cache = True
torch.set_grad_enabled(False)
print("✅ Modelo cargado")