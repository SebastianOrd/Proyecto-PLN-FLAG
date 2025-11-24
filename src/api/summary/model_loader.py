# src/api/summary/model_loader.py
import torch
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from google.cloud import storage

# Descargar modelos desde GCS si no existen
def download_from_gcs_if_needed():
    bucket_name = "proyecto-pln-flag-models"
    local_base_dir = "/tmp/models"
    
    # Crear directorios
    os.makedirs(f"{local_base_dir}/deepseek-coder-1p3b-lora-base", exist_ok=True)
    os.makedirs(f"{local_base_dir}/checkpoint-191", exist_ok=True)
    
    # Si ya existen, skip
    if os.path.exists(f"{local_base_dir}/deepseek-coder-1p3b-lora-base/config.json"):
        print("✅ Modelos ya descargados")
        return local_base_dir
    
    print("📥 Descargando modelos desde GCS...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Descargar modelo base
    blobs = bucket.list_blobs(prefix="deepseek-coder-1p3b-lora-base/")
    for blob in blobs:
        if not blob.name.endswith("/"):
            local_path = f"{local_base_dir}/{blob.name}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            blob.download_to_filename(local_path)
            print(f"  ✓ {blob.name}")
    
    # Descargar checkpoint LoRA
    blobs = bucket.list_blobs(prefix="checkpoint-191/")
    for blob in blobs:
        if not blob.name.endswith("/"):
            local_path = f"{local_base_dir}/{blob.name}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            blob.download_to_filename(local_path)
            print(f"  ✓ {blob.name}")
    
    print("✅ Modelos descargados")
    return local_base_dir

# Descargar modelos
BASE_DIR = download_from_gcs_if_needed()

MODEL_DIR = f"{BASE_DIR}/deepseek-coder-1p3b-lora-base"
CKPT_DIR = f"{BASE_DIR}/checkpoint-191"

print(f"🔍 Cargando tokenizer desde: {MODEL_DIR}")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR,
    use_fast=False,
    trust_remote_code=True,
    local_files_only=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

tokenizer.padding_side = "left"

print(f"🔍 Cargando modelo base...")

base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    device_map="cpu",
    torch_dtype=torch.float32,
    trust_remote_code=True,
    local_files_only=True
)

print(f"🔍 Montando adaptador LoRA desde: {CKPT_DIR}")

model = PeftModel.from_pretrained(base_model, CKPT_DIR)
model.eval()

print("✅ Modelo cargado")