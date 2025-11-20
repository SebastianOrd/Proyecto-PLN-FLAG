# src/api/metrics/inference.py

import numpy as np
import pandas as pd
import textstat
from bert_score import score as bert_score

from .model_loader import scorer_nli, scorer_bin, bert_scorer, device



def safe_float(x):
    try:
        x = float(x)
    except:
        return 0.0

    if np.isnan(x) or np.isinf(x):
        return 0.0
    return x


#FACTUALIDAD (AlignScore)
def calcular_factualidad_alignscore(preds, refs):
    preds = preds.tolist()
    refs = refs.tolist()

    #Score NLI y binario
    scores_nli = scorer_nli.score(contexts=refs, claims=preds)
    scores_bin = scorer_bin.score(contexts=refs, claims=preds)

    scores_nli = [safe_float(s) for s in scores_nli]
    scores_bin = [safe_float(s) for s in scores_bin]

    summary = {
        "mean_alignscore_nli": safe_float(np.mean(scores_nli)),
        "std_alignscore_nli": safe_float(np.std(scores_nli)),
        "min_alignscore_nli": safe_float(np.min(scores_nli)),
        "max_alignscore_nli": safe_float(np.max(scores_nli)),

        "mean_alignscore_bin": safe_float(np.mean(scores_bin)),
        "std_alignscore_bin": safe_float(np.std(scores_bin)),
        "min_alignscore_bin": safe_float(np.min(scores_bin)),
        "max_alignscore_bin": safe_float(np.max(scores_bin)),
    }

    return summary


#Relevancia
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

    p_list = [safe_float(p) for p in P]
    r_list = [safe_float(r) for r in R]
    f_list = [safe_float(f) for f in F1]

    return {
        "mean_precision": safe_float(np.mean(p_list)),
        "mean_recall": safe_float(np.mean(r_list)),
        "mean_f1": safe_float(np.mean(f_list)),
    }


#Legibilidad
def calcular_legibilidad_textstat(preds):
    rows = []
    for t in preds:
        t = t or ""
        row = {
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
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    summary = {f"mean_{col}": safe_float(df[col].mean()) for col in df.columns}
    summary["n_examples"] = len(preds)

    return summary


#Funcion principal para calcular las metricas
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