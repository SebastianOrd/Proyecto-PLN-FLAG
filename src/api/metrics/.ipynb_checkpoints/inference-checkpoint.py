# src/api/metrics/inference.py

import numpy as np
import pandas as pd
import textstat
import time
from .model_loader import bert_scorer, device

# -----------------------------------------------------------
# UTILIDAD GENERAL
# -----------------------------------------------------------
def safe_float(x):
    try:
        x = float(x)
    except:
        return 0.0
    if np.isnan(x) or np.isinf(x):
        return 0.0
    return x


# -----------------------------------------------------------
# 1) LEGIBILIDAD (muy rápido)
# -----------------------------------------------------------
def calcular_legibilidad_textstat(preds):
    # Convertir Series → list
    if isinstance(preds, pd.Series):
        preds = preds.tolist()

    rows = []
    for t in preds:
        t = t or ""
        rows.append({
            "flesch_reading_ease": safe_float(textstat.flesch_reading_ease(t)),
            "flesch_kincaid_grade": safe_float(textstat.flesch_kincaid_grade(t)),
            "gunning_fog": safe_float(textstat.gunning_fog(t)),
            "smog_index": safe_float(textstat.smog_index(t)) if textstat.sentence_count(t) >= 3 else 0.0,
            "dale_chall": safe_float(textstat.dale_chall_readability_score(t)),
            "automated_readability": safe_float(textstat.automated_readability_index(t)),
            "coleman_liau": safe_float(textstat.coleman_liau_index(t)),
            "num_sentences": int(textstat.sentence_count(t)),
            "num_words": int(textstat.lexicon_count(t, removepunct=True)),
            "syllables": int(textstat.syllable_count(t)),
            "reading_time_sec": safe_float(textstat.reading_time(t)),
        })

    df = pd.DataFrame(rows)
    summary = {f"mean_{col}": safe_float(df[col].mean()) for col in df.columns}
    summary["n_examples"] = len(preds)

    return summary


# -----------------------------------------------------------
# 2) RELEVANCIA (BERTScore usando scorer precargado)
# -----------------------------------------------------------
def calcular_relevancia_simple(preds, refs):
    # Asegurar listas
    if isinstance(preds, pd.Series):
        preds = preds.tolist()
    if isinstance(refs, pd.Series):
        refs = refs.tolist()

    # Usa el scorer precargado (mucho más rápido)
    P, R, F1 = bert_scorer(
        cands=preds,
        refs=refs,
        lang="en",
        model_type="roberta-base",
        idf=False,
        batch_size=1,
        device=device,
    )

    return {
        "mean_precision": float(P.mean()),
        "mean_recall": float(R.mean()),
        "mean_f1": float(F1.mean()),
    }


# -----------------------------------------------------------
# (OPCIONAL) 3) FACTUALIDAD — AlignScore
# -----------------------------------------------------------
# Dejamos AlignScore aquí, comentado y listo para usar cuando tengas GPU o tiempo.
#
# from .model_loader import scorer_nli
#
# def calcular_factualidad_alignscore(preds, refs):
#     if isinstance(preds, pd.Series):
#         preds = preds.tolist()
#     if isinstance(refs, pd.Series):
#         refs = refs.tolist()
#
#     scores_nli = scorer_nli.score(contexts=refs, claims=preds)
#     scores_nli = [safe_float(s) for s in scores_nli]
#
#     return {
#         "mean_alignscore_nli": safe_float(np.mean(scores_nli)),
#     }


# -----------------------------------------------------------
# 4) FUNCIÓN COMPLETA (NO STREAMING)
# -----------------------------------------------------------
def calcular_metricas(article: str, summary: str):
    print("iniciando calculo de metricas")
    t0 = time.perf_counter()

    preds = pd.Series([summary])
    refs = pd.Series([article])

    # legibilidad
    t_leg0 = time.perf_counter()
    legibilidad = calcular_legibilidad_textstat(preds)
    print(f"[METRICS] Legibilidad tardó {time.perf_counter() - t_leg0:.2f} s")

    # relevancia
    t_rel0 = time.perf_counter()
    relevancia = calcular_relevancia_simple(preds, refs)
    print(f"[METRICS] Relevancia (BERTScore) tardó {time.perf_counter() - t_rel0:.2f} s")

    # factualidad (desactivada a propósito)
    # t_fact0 = time.perf_counter()
    # factualidad = calcular_factualidad_alignscore(preds, refs)
    # print(f"[METRICS] Factualidad tardó {time.perf_counter() - t_fact0:.2f} s")

    print(f"[METRICS] TOTAL compute_metrics tardó {time.perf_counter() - t0:.2f} s")

    return {
        "legibilidad": legibilidad,
        "relevancia": relevancia,
        # "factualidad": factualidad,   # ← listo para activar cuando quieras
    }
