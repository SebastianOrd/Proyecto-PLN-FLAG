from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from threading import Thread
from transformers import TextIteratorStreamer

from .inference import build_prompt
from ..summary.model_loader import model, tokenizer    # Ajusta la ruta exacta

router = APIRouter(prefix="/summary", tags=["PLS Summary"])


class SummaryInput(BaseModel):
    text: str


@router.post("/")
def summarize(payload: SummaryInput):
    text = payload.text.strip()

    if not text:
        return {"error": "Empty text"}

    summary = generate_summary(text)
    return {"summary": summary}



# ----------------------------------------------------------------------
# 🚀 NUEVO ENDPOINT: STREAMING DE TOKENS
# ----------------------------------------------------------------------
@router.post("/stream/")
def summarize_stream(payload: SummaryInput):
    text = payload.text.strip()

    if not text:
        return StreamingResponse(iter(["Empty text"]), media_type="text/plain")

    prompt = build_prompt(text)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048,
        padding=True,
    )
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    streamer = TextIteratorStreamer(
        tokenizer,
        skip_prompt=True,          # ya lo tenías para no mostrar el prompt
        skip_special_tokens=True,
        decode_kwargs={"skip_special_tokens": True},
    )

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=50,        # lo que estés usando
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
        for new_text in streamer:
            if new_text:
                yield new_text
        # Cuando el streamer termina, mandamos un marcador explícito
        yield "\n<<END_OF_SUMMARY_STREAM>>"

    return StreamingResponse(token_generator(), media_type="text/plain")