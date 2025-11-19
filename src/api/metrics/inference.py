# src/api/metrics/inference.py

import numpy as np
import pandas as pd
import textstat
from bert_score import score as bert_score

from .model_loader import scorer_nli, scorer_bin, bert_scorer, device

# ==============================
# FACTUALIDAD (ALIGNSCORE)
# ==============================

def calcular_factualidad_alignscore(preds, refs):

    preds = preds.tolist()
    refs = refs.tolist()

    scores_nli = scorer_nli.score(contexts=refs, claims=preds)
    scores_bin = scorer_bin.score(contexts=refs, claims=preds)

    scores_nli = [float(s) for s in scores_nli]
    scores_bin = [float(s) for s in scores_bin]

    summary = {
        "mean_alignscore_nli": float(np.mean(scores_nli)),
        "std_alignscore_nli": float(np.std(scores_nli)),
        "min_alignscore_nli": float(np.min(scores_nli)),
        "max_alignscore_nli": float(np.max(scores_nli)),

        "mean_alignscore_bin": float(np.mean(scores_bin)),
        "std_alignscore_bin": float(np.std(scores_bin)),
        "min_alignscore_bin": float(np.min(scores_bin)),
        "max_alignscore_bin": float(np.max(scores_bin)),
    }

    return summary


# ==============================
# RELEVANCIA (BERTSCORE)
# ==============================

def calcular_bertscore_relevancia(preds, refs):

    P, R, F1 = bert_scorer(
        cands=preds.tolist(),
        refs=refs.tolist(),
        lang="en",
        model_type="roberta-base",
        idf=True,
        rescale_with_baseline=False,
        batch_size=1,
        device=device
    )

    return {
        "mean_precision": float(np.mean(P)),
        "mean_recall": float(np.mean(R)),
        "mean_f1": float(np.mean(F1))
    }


# ==============================
# LEGIBILIDAD (TEXTSTAT)
# ==============================

def calcular_legibilidad_textstat(preds):

    rows = []
    for t in preds:
        t = t or ""
        row = {
            "flesch_reading_ease": float(textstat.flesch_reading_ease(t)),
            "flesch_kincaid_grade": float(textstat.flesch_kincaid_grade(t)),
            "gunning_fog": float(textstat.gunning_fog(t)),
            "smog_index": float(textstat.smog_index(t)) if textstat.sentence_count(t) >= 3 else float("nan"),
            "dale_chall": float(textstat.dale_chall_readability_score(t)),
            "automated_readability": float(textstat.automated_readability_index(t)),
            "coleman_liau": float(textstat.coleman_liau_index(t)),
            "num_sentences": int(textstat.sentence_count(t)),
            "num_words": int(textstat.lexicon_count(t, removepunct=True)),
            "syllables": int(textstat.syllable_count(t)),
            "reading_time_sec": float(textstat.reading_time(t)),
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    summary = {
        f"mean_{col}": float(df[col].mean()) for col in df.columns
    }

    summary["n_examples"] = len(preds)

    return summary


# ==============================
# FUNCIÓN CENTRAL
# ==============================

def calcular_metricas(article: str, summary: str):
    preds = pd.Series([summary])
    refs = pd.Series([article])

    relevancia = calcular_bertscore_relevancia(preds, refs)
    legibilidad = calcular_legibilidad_textstat(preds)
    factualidad = calcular_factualidad_alignscore(preds, refs)

    return {
        "relevancia": relevancia,
        "legibilidad": legibilidad,
        "factualidad": factualidad
    }