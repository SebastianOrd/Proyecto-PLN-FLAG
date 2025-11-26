from __future__ import annotations
import json
import time
import os
import requests
from typing import Any, Dict, Tuple
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Endpoints de las APIs
API_CLASSIFY_URL = os.getenv("API_CLASSIFY_URL", "http://api-summary:8000/process")
API_SUMMARY_URL = os.getenv("API_SUMMARY_URL", "http://api-summary:8000/summary/")
API_SUMMARY_STREAM_URL = os.getenv("API_SUMMARY_STREAM_URL", "http://api-summary:8000/summary/stream/")
API_METRICS_URL = os.getenv("API_METRICS_URL", "http://api-metrics:8001/metrics")
API_METRICS_STREAM_URL = os.getenv(
    "API_METRICS_STREAM_URL",
    "http://api-metrics:8001/metrics/stream/"
)

def call_api(texto: str) -> Tuple[Dict[str, Any] | None, str | None]:
    """Llama a la API que realiza la clasificación."""
    t0 = time.perf_counter()
    try:
        r = requests.post(API_CLASSIFY_URL, json={"text": texto}, timeout=300)
        dt = time.perf_counter() - t0
        print(f"[UI] POST {API_CLASSIFY_URL} tardó {dt:.1f} s")

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


def call_api_summary(texto: str) -> Tuple[str | None, str | None]:
    """Llama al endpoint que genera el resumen PLS (modo normal, no streaming)."""
    t0 = time.perf_counter()
    try:
        r = requests.post(API_SUMMARY_URL, json={"text": texto}, timeout=600)
        dt = time.perf_counter() - t0
        print(f"[UI] POST {API_SUMMARY_URL} tardó {dt:.1f} s")

        if r.status_code != 200:
            return None, f"Error al comunicarse con la API de resumen: {r.status_code}"

        data = r.json()
        if "error" in data:
            return None, data["error"]

        return data["summary"], None

    except requests.exceptions.ConnectionError as e:
        return None, f"Error de conexión con la API de resumen: {e}"
    except requests.exceptions.Timeout:
        return None, "Timeout: La API de resumen tardó demasiado (>10 min)"
    except Exception as e:
        return None, f"Error de conexión con la API de resumen: {e}"


def call_api_metrics(original: str, summary: str):
    """Llama a la API de métricas."""
    t0 = time.perf_counter()
    try:
        r = requests.post(
            API_METRICS_URL,
            json={"original_text": original, "summary_text": summary},
            timeout=600,
        )
        dt = time.perf_counter() - t0
        print(f"[UI] POST {API_METRICS_URL} tardó {dt:.1f} s")

        if r.status_code != 200:
            return None, f"Error en API de métricas: {r.status_code}"

        data = r.json()
        return data, None

    except requests.exceptions.ConnectionError as e:
        return None, f"Error de conexión con API de métricas: {e}"
    except requests.exceptions.Timeout:
        return None, "Timeout: La API de métricas tardó demasiado (>10 min)"
    except Exception as e:
        return None, f"Error de conexión con API de métricas: {e}"


def call_api_summary_stream(text: str):
    """
    Llama al endpoint de streaming y va devolviendo el texto parcial (chunks).
    Esto NO sabe nada de Streamlit, solo yield de texto.
    """
    with requests.post(
        API_SUMMARY_STREAM_URL,
        json={"text": text},
        stream=True,
    ) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk
def call_api_metrics_stream(original: str, summary: str):

    with requests.post(
        API_METRICS_STREAM_URL,
        json={"original_text": original, "summary_text": summary},
        stream=True,
    ) as r:
        r.raise_for_status()

        for raw in r.iter_lines(decode_unicode=True):

            if not raw:
                continue  # ← IGNORAR líneas vacías

            line = raw.strip()
            if not line:
                continue  # ← IGNORAR whitespace

            if not line.startswith("{"):
                print(f"[UI] Chunk ignorado (no JSON): {line}")
                continue

            try:
                event = json.loads(line)
                yield event
            except Exception as e:
                print(f"[UI] Error parseando chunk: {e}")
                print(f"[UI] Chunk recibido: {repr(line)}")
                continue
