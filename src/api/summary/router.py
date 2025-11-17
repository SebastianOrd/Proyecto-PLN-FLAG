# src/api/summary/router.py

from fastapi import APIRouter
from pydantic import BaseModel
from .inference import generate_summary

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