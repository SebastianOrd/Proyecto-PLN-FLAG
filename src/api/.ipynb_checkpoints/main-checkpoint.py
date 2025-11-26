        # src/api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import joblib
import os
from google.cloud import storage

# FIX para cargar classifier_sparse.joblib
import sys
import types

class TextPreprocessor:
    def clean_light_text(self, text):
        return text

    def tokenize(self, text):
        return text.split()
        
main_module = types.ModuleType("__main__")
main_module.TextPreprocessor = TextPreprocessor

_textproc = TextPreprocessor()
main_module.clean_light_text = _textproc.clean_light_text
main_module.tokenize = _textproc.tokenize

sys.modules["__main__"] = main_module

# Router de resumen
from src.api.summary.router import router as summary_router

app = FastAPI(title="BioLaySumm API")
app.include_router(summary_router)

# Descargar clasificador desde GCS
def download_classifier():
    local_path = "/app/modelos/classifier_sparse_ridge_calibrated.joblib"
    
    if os.path.exists(local_path):
        print("✅ Clasificador ya descargado")
        return local_path
    
    print("📥 Descargando clasificador desde GCS...")
    client = storage.Client()
    bucket = client.bucket("proyecto-pln-flag-models")
    blob = bucket.blob("classifier/classifier_sparse_ridge_calibrated.joblib")
    blob.download_to_filename(local_path)
    print("✅ Clasificador descargado")
    
    return local_path

CLASSIFIER_PATH = download_classifier()
classifier_model = joblib.load(CLASSIFIER_PATH)

# Request body
class InputText(BaseModel):
    text: str

# Endpoint de clasificacion
@app.post("/process")
def process_text(payload: InputText):
    texto = payload.text.strip()
    if not texto:
        return {"error": "Texto vacío"}

    pred = classifier_model.predict([texto])[0]
    probs = classifier_model.predict_proba([texto])[0]
    confianza = float(probs[pred])
    etiqueta = "Científico" if pred == 0 else "No científico"

    return {
        "classification": {
            "label": etiqueta,
            "confidence": confianza
        }
    }

# Levantar el server
if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True, access_log=True)