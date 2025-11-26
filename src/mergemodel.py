from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from pathlib import Path
import torch

BASE_MODEL_ID = "deepseek-ai/deepseek-coder-1.3b-base"
LORA_ADAPTER_PATH = "modelos/deepseek-coder-1p3b-lora"
OUT_PATH = Path("modelos/deepseek-coder-1p3b-merged")

OUT_PATH.mkdir(parents=True, exist_ok=True)

print("🔹 Cargando modelo base en float16 con low_cpu_mem_usage...")
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    trust_remote_code=True,
    torch_dtype=torch.float16,      # reduce memoria
    low_cpu_mem_usage=True,         # reduce pico de RAM
    device_map="cpu",               # todo en CPU
)

print("🔹 Cargando adaptador LoRA...")
model = PeftModel.from_pretrained(
    model,
    LORA_ADAPTER_PATH,
)

print("🔹 Haciendo merge de LoRA en el modelo base...")
model = model.merge_and_unload()
model.config.torch_dtype = torch.float16   # dejar marcado en la config

print(f"💾 Guardando modelo fusionado en {OUT_PATH}...")
model.save_pretrained(OUT_PATH)

print("🔹 Guardando tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL_ID,
    trust_remote_code=True,
)
tokenizer.save_pretrained(OUT_PATH)

print("✅ Merge completado correctamente")
