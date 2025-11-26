from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import json
import time
import pandas as pd

from .inference import (
    calcular_metricas,
    calcular_legibilidad_textstat,
    calcular_relevancia_simple,
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


class MetricsInput(BaseModel):
    article: str
    summary: str


# ----------------------------------------
#    ENDPOINT NORMAL
# ----------------------------------------
@router.post("/calculate")
def calculate_metrics(payload: MetricsInput):
    if not payload.article or not payload.summary:
        raise HTTPException(status_code=400, detail="Article and summary are required.")
    
    return calcular_metricas(
        article=payload.article,
        summary=payload.summary
    )


# ----------------------------------------
#         ENDPOINT STREAMING SSE
# ----------------------------------------
@router.post("/stream")
def metrics_stream(payload: MetricsInput):

    original = payload.article or ""
    summary = payload.summary or ""

    def gen():

        # 1) Legibilidad
        t0 = time.perf_counter()
        leg_data = calcular_legibilidad_textstat(pd.Series([summary]))
        dt = time.perf_counter() - t0
        print(f"[METRICS-STREAM] Legibilidad tardó {dt:.2f} s")

        yield (
            "data: " + json.dumps({
                "type": "legibilidad",
                "data": leg_data
            }) + "\n\n"
        )

        # 2) Relevancia
        t1 = time.perf_counter()
        rel_data = calcular_relevancia_simple(
            pd.Series([summary]),
            pd.Series([original])
        )
        dt = time.perf_counter() - t1
        print(f"[METRICS-STREAM] Relevancia tardó {dt:.2f} s")

        yield (
            "data: " + json.dumps({
                "type": "relevancia",
                "data": rel_data
            }) + "\n\n"
        )

        # 3) Señal de finalización
        yield "data: " + json.dumps({"type": "done"}) + "\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
