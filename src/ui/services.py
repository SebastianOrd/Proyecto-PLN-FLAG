from __future__ import annotations

import time
import os
import joblib
import requests
from typing import Any, Dict, Tuple
from sklearn.metrics import precision_score, recall_score, f1_score
import sys
import types

#
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)


#Enpoints de las APIs
API_CLASSIFY_URL = "http://127.0.0.1:8000/process"      # Clasificación
API_SUMMARY_URL  = "http://127.0.0.1:8000/summary"      # Resumen PLS


#Llamada a API para clasificar
def call_api(texto: str) -> Tuple[Dict[str, Any] | None, str | None]:
    """
    Llama a la API que realiza la clasificación.
    """
    try:
        r = requests.post(API_CLASSIFY_URL, json={"text": texto})

        if r.status_code != 200:
            return None, "Error al comunicarse con la API"

        data = r.json()

        if "error" in data:
            return None, data["error"]

        print("API respuesta:", data)
        return data, None

    except Exception as e:
        return None, f"Error de conexión con la API: {e}"


#Llamar a la API para resumir
def call_api_summary(texto: str) -> Tuple[str | None, str | None]:
    """
    Llama al endpoint que genera el resumen PLS.
    Devuelve:
      - resumen en texto plano
      - error (si aplica)
    """
    try:
        r = requests.post(API_SUMMARY_URL, json={"text": texto})

        if r.status_code != 200:
            return None, "Error al comunicarse con la API de resumen"

        data = r.json()

        if "error" in data:
            return None, data["error"]

        return data["summary"], None

    except Exception as e:
        return None, f"Error de conexión con la API de resumen: {e}"