# src/ui/storage.py
from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json
import threading

# Archivo "mini base de datos" dentro del contenedor
LOG_PATH = Path("/tmp/biolaysumm_runs.jsonl")

_lock = threading.Lock()


def log_run(record: Dict[str, Any]) -> None:
    """
    Guarda un resumen y sus métricas como una línea JSON.
    No falla si el directorio/archivo no existe.
    """
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    payload = dict(record)
    # timestamp estándar
    payload.setdefault("timestamp", datetime.utcnow().isoformat())

    line = json.dumps(payload, ensure_ascii=False)

    with _lock:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def load_runs() -> List[Dict[str, Any]]:
    """
    Lee todos los registros guardados. Lista de dicts.
    Si no existe el archivo, devuelve [].
    """
    if not LOG_PATH.exists():
        return []

    runs: List[Dict[str, Any]] = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                runs.append(json.loads(raw))
            except Exception:
                # si una línea está corrupta, la saltamos
                continue
    return runs