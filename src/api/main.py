from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import joblib
import os


#FIX para cargar classifier_sparse.joblib
import sys
import types
from src.models.classifier.sparse.text_preprocessor import TextPreprocessor

main_module = types.ModuleType("__main__")
main_module.TextPreprocessor = TextPreprocessor

_textproc = TextPreprocessor()
main_module.clean_light_text = _textproc.clean_light_text
main_module.tokenize = _textproc.tokenize

sys.modules["__main__"] = main_module


#Router de resusmen

from src.api.summary.router import router as summary_router
#from src.api.metrics.router import router as metrics_router

app = FastAPI(title="BioLaySumm API")
app.include_router(summary_router)
#app.include_router(metrics_router)

#Cargar clasificador v2 100% real no fake.
CLASSIFIER_PATH = os.path.join(
    "src",
    "models",
    "classifier",
    "sparse",
    "classifier_sparse_ridge_calibrated.joblib"   #nuevo joblib con confidence
)

classifier_model = joblib.load(CLASSIFIER_PATH)


#Request body

class InputText(BaseModel):
    text: str


#Endpoint de clasificacion

@app.post("/process")
def process_text(payload: InputText):
    texto = payload.text.strip()
    if not texto:
        return {"error": "Texto vacío"}

    #Prediccion
    pred = classifier_model.predict([texto])[0]

    #Probabilidades
    probs = classifier_model.predict_proba([texto])[0]

    #Clases del modelo
    clases = classifier_model.classes_

    #Probabilidad de la clase predicha
    confianza = float(probs[pred])

    #Dejamos estas para el debug:
    confianza_predicha = confianza
    confianza_clase1 = float(probs[1])

    etiqueta = "Científico" if pred == 0 else "No científico"

    #Debugging clasificador
    #print("\n============== DEBUG CLASIFICADOR ==============")
    #print("Texto analizado:", texto[:200], "...")
    #print("Clases del modelo:", clases)
    #print("Predicción (índice):", pred)
    #print("Predicción (label):", etiqueta)
    #print("Probabilidades crudas predict_proba:", probs)
    #print("Probabilidad de la clase predicha:", confianza_predicha)
    #print("Probabilidad clase 1:", confianza_clase1)
    #print("=================================================\n")

    return {
        "classification": {
            "label": etiqueta,
            "confidence": confianza
        }
    }

#Levantar el server
if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True, access_log=True)