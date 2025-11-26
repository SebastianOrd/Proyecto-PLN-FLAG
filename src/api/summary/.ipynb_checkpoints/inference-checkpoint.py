import torch
from .model_loader import model, tokenizer
import time


def build_prompt(scientific_text: str) -> str:
    return f"""You are a medical writer.
Summarize the following biomedical abstract as a Plain Language Summary (PLS) for any patient.
Use this structure exactly:
1. Plain Title
2. Rationale
3. Trial Design
4. Results
Write short sentences (≤15 words) in active voice with simple words.
Explain any medical terms briefly.
Do not invent or assume data not in the abstract.

Abstract:
{scientific_text}

PLS:
Plain Title:
Rationale:
Trial Design:
Results:
"""


@torch.inference_mode()
def generate_summary(text: str):
    t0 = time.perf_counter()
    t_prompt0 = time.perf_counter()
    prompt = build_prompt(text)
    print(f"[SUMMARY] Construcción de prompt tardó {time.perf_counter() - t_prompt0:.2f} s")
    t_tok0 = time.perf_counter()
    encoded = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=2048 - 300,  #deja espacio para generar
    )
    print(f"[SUMMARY] Tokenización tardó {time.perf_counter() - t_tok0:.2f} s")

    input_ids = encoded["input_ids"].to(model.device)
    attention_mask = encoded["attention_mask"].to(model.device)
    t_gen0 = time.perf_counter()
    gen_ids = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_new_tokens=380,
        temperature=0.0,
        top_p=1.0,
        num_beams=1,
        no_repeat_ngram_size=4,
        use_cache=True,           # por si acaso, debería estar en True
        repetition_penalty=1.02,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
    )
    print(f"[SUMMARY] model.generate tardó {time.perf_counter() - t_gen0:.2f} s")

    #Cortar lo generado
    input_len = attention_mask.sum(dim=1)[0]
    gen_only = gen_ids[0, input_len:]

    summary = tokenizer.decode(gen_only, skip_special_tokens=True).strip()

    return summary