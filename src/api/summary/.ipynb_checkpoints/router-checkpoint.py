from fastapi import APIRouter
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from threading import Thread, Lock
from transformers import TextIteratorStreamer

from .inference import build_prompt
from ..summary.model_loader import model, tokenizer    # Ajusta la ruta exacta

router = APIRouter(prefix="/summary", tags=["PLS Summary"])
summary_lock = Lock()


class SummaryInput(BaseModel):
    text: str


@router.post("/")
def summarize(payload: SummaryInput):
    text = payload.text.strip()
    if not text:
        return {"error": "Empty text"}

    # Intentar tomar el lock SIN bloquear
    if not summary_lock.acquire(blocking=False):
        # Ya hay una generación en curso → devolvemos 429
        return PlainTextResponse(
            "BUSY: El modelo está procesando otra solicitud. Intenta en unos segundos.",
            status_code=429,
        )

    try:
        summary = generate_summary(text)
        return {"summary": summary}
    finally:
        summary_lock.release()


# ----------------------------------------------------------------------
# 🚀 NUEVO ENDPOINT: STREAMING DE TOKENS
# ----------------------------------------------------------------------
@router.post("/stream/")
def summarize_stream(payload: SummaryInput):
    text = payload.text.strip()

    if not text:
        return StreamingResponse(iter(["Empty text"]), media_type="text/plain")
    if not summary_lock.acquire(blocking=False):
        # Ya hay una generación en curso → devolvemos error plano 429
        return PlainTextResponse(
            "BUSY: El modelo está procesando otra solicitud. Intenta en unos segundos.",
            status_code=429,
        )
    prompt = build_prompt(text)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048,
        padding=True,
    )
    print("MODEL DEVICE:", model.device)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    streamer = TextIteratorStreamer(
        tokenizer,
        skip_prompt=True,          #  no mostrar el prompt
        skip_special_tokens=True,
        decode_kwargs={"skip_special_tokens": True},
    )

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=380,        # lo que estés usando
        temperature=0.0,
        top_p=1.0,
        num_beams=1,
        no_repeat_ngram_size=4,
        repetition_penalty=1.02,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        use_cache=True,
    )

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    def token_generator():
        # Emitimos texto a medida que llega
        try:
            for new_text in streamer:
                if new_text:
                    yield new_text
            # Cuando el streamer termina, mandamos un marcador explícito
            yield "\n<<END_OF_SUMMARY_STREAM>>"
        finally:
            summary_lock.release()
    return StreamingResponse(token_generator(), media_type="text/plain")