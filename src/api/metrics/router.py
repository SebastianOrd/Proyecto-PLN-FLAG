from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .inference import calcular_metricas

router = APIRouter(prefix="/metrics", tags=["Metrics"])

class MetricsInput(BaseModel):
    article: str
    summary: str

@router.post("/calculate")
def calculate_metrics(payload: MetricsInput):
    if not payload.article or not payload.summary:
        raise HTTPException(status_code=400, detail="Article and summary are required.")

    result = calcular_metricas(payload.article, payload.summary)
    return result