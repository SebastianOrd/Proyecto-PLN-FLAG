# src/api/metrics/model_loader.py

import torch
from alignscore import AlignScore
from bert_score import score as bert_score
import textstat
import os

#Config

ALIGN_CKPT_PATH = os.path.join(
    "modelos", "alignscore", "AlignScore-large.ckpt"
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("MODEL METRICS DEVICE:", device)

#Carga de modelos

#AlignScore NLI
scorer_nli = AlignScore(
    model="roberta-large",
    batch_size=1,
    device=device,
    ckpt_path=ALIGN_CKPT_PATH,
    evaluation_mode="nli_sp"
)
# Intento de optimización FP16 si hay GPU
if device.type == "cuda":
    try:
        # Estructura típica: scorer.model.model.model (AlignScore → Inferencer → HF model)
        scorer_nli.model.model.model.half()
        print("[METRICS] AlignScore pasado a FP16 en GPU.")
    except AttributeError:
        print("[METRICS] No se pudo aplicar FP16 automáticamente; se usará FP32 normal.")

#BERTScore scorer
bert_scorer = bert_score  #wrapper simple

#textstat (legibilidad)
textstat.set_lang("en")