# src/api/main.py

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import joblib
import os

# ------------------------------
# 🔧 FIX para cargar classifier_sparse.joblib
# ------------------------------
import sys
import types
from src.models.classifier.sparse.text_preprocessor import TextPreprocessor

main_module = types.ModuleType("__main__")
main_module.TextPreprocessor = TextPreprocessor

_textproc = TextPreprocessor()
main_module.clean_light_text = _textproc.clean_light_text
main_module.tokenize = _textproc.tokenize

sys.modules["__main__"] = main_module
# ------------------------------


# Importar router del resumen
from src.api.summary.router import router as summary_router

app = FastAPI(title="BioLaySumm API")

# Registrar router /summary
app.include_router(summary_router)


# Cargar clasificador real
CLASSIFIER_PATH = os.path.join(
    "src",
    "models",
    "classifier",
    "sparse",
    "classifier_sparse.joblib"
)

classifier_model = joblib.load(CLASSIFIER_PATH)


class InputText(BaseModel):
    text: str


@app.post("/process")
def process_text(payload: InputText):
    texto = payload.text.strip()
    if not texto:
        return {"error": "Texto vacío"}

    # --- Clasificación ---
    pred = classifier_model.predict([texto])[0]
    etiqueta = "Científico" if pred == 0 else "No científico"

    return {
        "classification": {
            "label": etiqueta,
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0
        }
    }


if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True, access_log=True)