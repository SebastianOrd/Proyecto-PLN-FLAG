import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os

#Rutas base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models",
    "deepseek-coder-1p3b-lora-base"   #modelo base descargado (no se sube al repo por el peso)
)

CKPT_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "deepseek-coder-1p3b-qlora",
    "checkpoint-191"                 #adaptador LoRa entrenado
)

print("🔍 Cargando tokenizer desde:", MODEL_DIR)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR,
    use_fast=True,
    trust_remote_code=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

tokenizer.padding_side = "left"

print("🔍 Cargando modelo base (CPU, sin bitsandbytes)...")

#IMPORTANTE → sin 4-bit, sin bitsandbytes por mi GPU AMD (Brayan Gómez)
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    device_map="cpu",           #obligatorio para AMD
    torch_dtype=torch.float32,  #float16 en CPU puede romper
    trust_remote_code=True
)

print("🔍 Montando adaptador LoRA desde:", CKPT_DIR)

model = PeftModel.from_pretrained(base_model, CKPT_DIR)
model.eval()

print("✅ Modelo de resumen cargado correctamente en CPU (AMD compatible)")