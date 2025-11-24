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


# Endpoints de las APIs
# IMPORTANTE: Usar nombres de servicios Docker en lugar de 127.0.0.1
# Los contenedores se comunican por nombres, no por localhost
API_CLASSIFY_URL = os.getenv("API_CLASSIFY_URL", "http://api-summary:8000/process")
API_SUMMARY_URL  = os.getenv("API_SUMMARY_URL", "http://api-summary:8000/summary/")
API_METRICS_URL = os.getenv("API_METRICS_URL", "http://api-metrics:8001/metrics/")

# Para desarrollo local (sin Docker), configura estas variables de entorno:
# export API_CLASSIFY_URL=http://127.0.0.1:8000/process
# export API_SUMMARY_URL=http://127.0.0.1:8000/summary
# export API_METRICS_URL=http://127.0.0.1:8001/metrics


#Llamada a API para clasificar
def call_api(texto: str) -> Tuple[Dict[str, Any] | None, str | None]:
    """
    Llama a la API que realiza la clasificación.
    """
    try:
        r = requests.post(API_CLASSIFY_URL, json={"text": texto}, timeout=120)  # 2 minutos

        if r.status_code != 200:
            return None, f"Error al comunicarse con la API: {r.status_code}"

        data = r.json()

        if "error" in data:
            return None, data["error"]

        print("API respuesta:", data)
        return data, None

    except requests.exceptions.ConnectionError as e:
        return None, f"Error de conexión con la API: {e}"
    except requests.exceptions.Timeout:
        return None, "Timeout: La API tardó demasiado en responder (>2 min)"
    except Exception as e:
        return None, f"Error inesperado: {e}"


#Llamar a la API para resumir
def call_api_summary(texto: str) -> Tuple[str | None, str | None]:
    """
    Llama al endpoint que genera el resumen PLS.
    Devuelve:
      - resumen en texto plano
      - error (si aplica)
    """
    try:
        r = requests.post(API_SUMMARY_URL, json={"text": texto}, timeout=300)  # 5 minutos

        if r.status_code != 200:
            return None, f"Error al comunicarse con la API de resumen: {r.status_code}"

        data = r.json()

        if "error" in data:
            return None, data["error"]

        return data["summary"], None

    except requests.exceptions.ConnectionError as e:
        return None, f"Error de conexión con la API de resumen: {e}"
    except requests.exceptions.Timeout:
        return None, "Timeout: La API de resumen tardó demasiado (>5 min)"
    except Exception as e:
        return None, f"Error de conexión con la API de resumen: {e}"
    


#llamar a la  API para calcular metricas
def call_api_metrics(original: str, summary: str):
    """
    Llama a la API de métricas (se requiere Python 3.10 - ver requirements.txt).
    """
    try:
        r = requests.post(API_METRICS_URL, json={
            "original_text": original,
            "summary_text": summary
        }, timeout=300)  # 5 minutos

        if r.status_code != 200:
            return None, f"Error en API de métricas: {r.status_code}"

        data = r.json()
        return data, None

    except requests.exceptions.ConnectionError as e:
        return None, f"Error de conexión con API de métricas: {e}"
    except requests.exceptions.Timeout:
        return None, "Timeout: La API de métricas tardó demasiado (>5 min)"
    except Exception as e:
        return None, f"Error de conexión con API de métricas: {e}"