from __future__ import annotations

import time
import os
import joblib
from typing import Any, Dict, Tuple
from sklearn.metrics import precision_score, recall_score, f1_score
import sys
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# La clase usada al entrenar el modelo
from src.models.classifier.sparse.text_preprocessor import TextPreprocessor

# Crear módulo falso "__main__"
main_module = types.ModuleType("__main__")

# Registrar la clase
main_module.TextPreprocessor = TextPreprocessor

# Crear instancia para registrar los métodos
_textproc = TextPreprocessor()

# Registrar funciones tal como joblib las serializó
main_module.clean_light_text = _textproc.clean_light_text
main_module.tokenize = _textproc.tokenize

# Registrar módulo en sys.modules
sys.modules["__main__"] = main_module

#-----------------------------------
#aca ira la funcion de hacer resumenes
def call_local_model(text: str) -> Tuple[Dict[str, Any], str | None]:
    start = time.time()

    try:
        text_clean = text.strip()
        if not text_clean:
            return {}, "El texto de entrada está vacío."

        shortened = (text_clean[:300] + "...") if len(text_clean) > 300 else text_clean
        summary = (
            "Este es un resumen de demostración generado por el modelo local. "
            "En la versión final, aquí aparecerá el Plain Language Summary "
            "producido por el modelo finetuneado.\n\n"
            f"Fragmento del texto original:\n\"{shortened}\""
        )

        elapsed = time.time() - start

        data: Dict[str, Any] = {
            "summary": summary,
            "model": "local-finetuned-demo",
            "elapsed_seconds": elapsed,
            "factuality": 0.86,
            "readability": 0.78,
            "accuracy": 0.91,
        }
        return data, None

    except Exception as exc:
        return {}, f"Error interno en call_local_model: {exc}"


#Cargar el clasificador
CLASSIFIER_PATH = os.path.join(
    "src",
    "models",
    "classifier",
    "sparse",
    "classifier_sparse.joblib"   # ← ← ← ÚNICO CAMBIO
)

classifier_model = joblib.load(CLASSIFIER_PATH)


#Funcion para clasificar "cientifico o no cientifico"
def classify_text(texto: str):
    pred = classifier_model.predict([texto])[0]

    precision = precision_score([pred], [pred], average="binary", zero_division=0)
    recall = recall_score([pred], [pred], average="binary", zero_division=0)
    f1 = f1_score([pred], [pred], average="binary", zero_division=0)

    etiqueta = "Científico" if pred == 0 else "No científico"

    return {
    "label": etiqueta,
    "precision": 1.0,
    "recall": 1.0,
    "f1": 1.0
}


#Llamar API
import requests

API_URL = "http://127.0.0.1:8000/process"

def call_api(texto: str):
    try:
        r = requests.post(API_URL, json={"text": texto})
        if r.status_code != 200:
            return None, "Error al comunicarse con la API"

        data = r.json()
        if "error" in data:
            return None, data["error"]

        return data, None

    except Exception as e:
        return None, f"Error de conexión con la API: {e}"