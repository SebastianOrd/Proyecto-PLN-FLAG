from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from .inference import calcular_metricas

router = APIRouter(tags=["Metrics"])

class MetricsInput(BaseModel):
    original_text: str
    summary_text: str

@router.post("/metrics", summary="Calculate Metrics for Summary")
def metrics_endpoint(payload: MetricsInput):
    return calcular_metricas(
        article=payload.original_text,
        summary=payload.summary_text
    )

#App principal
app = FastAPI(title="Metrics API")

#Incluir router
app.include_router(router)