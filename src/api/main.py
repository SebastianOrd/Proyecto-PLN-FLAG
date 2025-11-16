from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from src.ui.services import classify_text, call_local_model

app = FastAPI(title="BioLaySumm API")

class InputText(BaseModel):
    text: str

@app.post("/process")
def process_text(payload: InputText):

    texto = payload.text.strip()

    #Clasificación
    clasificacion = classify_text(texto)

    #Resumen y métricas
    data, error = call_local_model(texto)

    if error:
        return {"error": error}

    return {
        "classification": clasificacion,
        "summary": data["summary"],
        "metrics": {
            "legibilidad": data["readability"],
            "factibilidad": data["factuality"],
            "accuracy": data["accuracy"],
        }
    }

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)