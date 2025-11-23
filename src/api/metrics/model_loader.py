# src/api/metrics/model_loader.py

import torch
from alignscore import AlignScore
from bert_score import score as bert_score
import textstat
import os

#Config

ALIGN_CKPT_PATH = os.path.join(
    "src", "models", "alignscore", "AlignScore-large.ckpt"
)

device = torch.device("cpu")

#Carga de modelos

#AlignScore NLI
scorer_nli = AlignScore(
    model="roberta-large",
    batch_size=1,
    device=device,
    ckpt_path=ALIGN_CKPT_PATH,
    evaluation_mode="nli_sp"
)

#AlignScore BINARIO
scorer_bin = AlignScore(
    model="roberta-large",
    batch_size=1,
    device=device,
    ckpt_path=ALIGN_CKPT_PATH,
    evaluation_mode="bin_sp"
)

#BERTScore scorer
bert_scorer = bert_score  #wrapper simple

#textstat (legibilidad)
textstat.set_lang("en")