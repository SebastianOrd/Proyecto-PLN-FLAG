from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, PlainTextResponse  # ← AÑADIR PlainTextResponse
import threading  
import json
import time
import pandas as pd

# Importa todas las funciones necesarias
from .inference import (
    calcular_metricas,
    calcular_legibilidad_textstat,
    calcular_relevancia_simple,
    calcular_factualidad_alignscore
)

router = APIRouter(tags=["Metrics"])

metrics_lock = threading.Lock()

# -----------------------------
#        MODELO DE INPUT
# -----------------------------
class MetricsInput(BaseModel):
    original_text: str
    summary_text: str


# -----------------------------
#    ENDPOINT NORMAL (NO STREAM)
# -----------------------------
@router.post("/metrics", summary="Calculate Metrics for Summary")
def metrics_endpoint(payload: MetricsInput):
    return calcular_metricas(
        article=payload.original_text,
        summary=payload.summary_text
    )


# -----------------------------
#    ENDPOINT STREAMING SSE
# -----------------------------
@router.post("/metrics/stream", summary="Streaming Metrics")
def metrics_stream(payload: MetricsInput):

    original = payload.original_text or ""
    summary = payload.summary_text or ""
    if not original or not summary:
        return PlainTextResponse("Empty fields", status_code=400)
    if not metrics_lock.acquire(blocking=False):
        return PlainTextResponse(
            "BUSY: El servidor está calculando métricas de otro resumen. Intenta nuevamente en unos segundos.",
            status_code=429,
        )
    # Generador SSE
    def generator():
        try:
            # ---------- 1) Legibilidad ----------
            t0 = time.perf_counter()
            leg_data = calcular_legibilidad_textstat(pd.Series([summary]))
            dt = time.perf_counter() - t0
            print(f"[METRICS-STREAM] Legibilidad tardó {dt:.2f} s")
    
            yield "data: " + json.dumps({
                "type": "legibilidad",
                "data": leg_data,
            }) + "\n\n"
    
            # ---------- 2) Relevancia ----------
            t1 = time.perf_counter()
            rel_data = calcular_relevancia_simple(
                pd.Series([summary]),
                pd.Series([original])
            )
            dt = time.perf_counter() - t1
            print(f"[METRICS-STREAM] Relevancia tardó {dt:.2f} s")
    
            yield "data: " + json.dumps({
                "type": "relevancia",
                "data": rel_data,
            }) + "\n\n"
    
            # 3) Factualidad con AlignScore
            t2 = time.perf_counter()
            fact_data = calcular_factualidad_alignscore(
                pd.Series([summary]),
                pd.Series([original])
            )
            dt = time.perf_counter() - t2
            print(f"[METRICS-STREAM] AlignScore tardó {dt:.2f} s")
    
            yield (
                "data: " + json.dumps({
                    "type": "factualidad",
                    "data": fact_data
                }) + "\n\n"
            )
    
            # 4) Señal de finalización
            yield "data: " + json.dumps({"type": "done"}) + "\n\n"
        finally:
            metrics_lock.release()
    # **CAMBIO IMPORTANTE**
    return StreamingResponse(generator(), media_type="text/event-stream")


# -----------------------------
#    FASTAPI APP PRINCIPAL
# -----------------------------
app = FastAPI(title="Metrics API")
app.include_router(router)
