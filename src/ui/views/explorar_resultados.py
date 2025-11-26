import streamlit as st
from storage import load_runs  
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
UI_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))  # src/ui

if UI_DIR not in sys.path:
    sys.path.append(UI_DIR)

from storage import load_runs   

def render():
    st.title("Explorar resultados generados")

    runs = load_runs()

    if not runs:
        st.info(
            "Aún no se han generado resúmenes en esta sesión del contenedor. "
            "Cuando generes algunos, aparecerán aquí."
        )
        return

    # Aplanar algunos campos para mostrarlos como tabla
    rows = []
    for i, r in enumerate(runs):
        leg = r.get("metrics_legibilidad") or {}
        rel = r.get("metrics_relevancia") or {}
        fact = r.get("metrics_factualidad") or {}

        rows.append(
            {
                "id": i,
                "timestamp": r.get("timestamp"),
                "tipo_texto": r.get("classification_label"),
                "conf_clf": r.get("classification_confidence"),
                "FRE": leg.get("mean_flesch_reading_ease"),
                "FK_grade": leg.get("mean_flesch_kincaid_grade"),
                "F1_relevancia": rel.get("mean_f1"),
                "AlignScore_NLI": fact.get("mean_alignscore_nli"),
            }
        )

    # Tabla resumen
    st.subheader("Historial de resúmenes")
    st.dataframe(rows, use_container_width=True)

    # Selector para ver detalle de un run
    st.subheader("Detalle de un resumen")
    idx = st.number_input(
        "Selecciona el ID de resumen",
        min_value=0,
        max_value=len(runs) - 1,
        value=len(runs) - 1,
        step=1,
    )

    r = runs[int(idx)]
    st.markdown("#### Texto original")
    st.write(r.get("original_text", ""))

    st.markdown("#### Resumen generado")
    st.write(r.get("summary_text", ""))

    st.markdown("#### Métricas de legibilidad")
    st.json(r.get("metrics_legibilidad") or {})

    st.markdown("#### Métricas de relevancia")
    st.json(r.get("metrics_relevancia") or {})

    if r.get("metrics_factualidad") is not None:
        st.markdown("#### Métricas de factualidad")
        st.json(r.get("metrics_factualidad") or {})