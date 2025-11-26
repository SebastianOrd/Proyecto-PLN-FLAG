from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

import json
import time
import pandas as pd

# Importa todas las funciones necesarias
from .inference import (
    calcular_metricas,
    calcular_legibilidad_textstat,
    calcular_relevancia_simple,
)

router = APIRouter(tags=["Metrics"])


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

    # Generador SSE
    def generator():

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

        # ---------- 3) Señal de FIN ----------
        yield "data: " + json.dumps({"type": "done"}) + "\n\n"

    # **CAMBIO IMPORTANTE**
    return StreamingResponse(generator(), media_type="text/event-stream")


# -----------------------------
#    FASTAPI APP PRINCIPAL
# -----------------------------
app = FastAPI(title="Metrics API")
app.include_router(router)
