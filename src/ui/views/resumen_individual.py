import streamlit as st
from src.ui.services import call_local_model, classify_text


def render():
    if "texto_resumen" not in st.session_state:
        st.session_state["texto_resumen"] = ""
    if "metricas" not in st.session_state:
        st.session_state["metricas"] = None
    if "metricas_clasificacion" not in st.session_state:
        st.session_state["metricas_clasificacion"] = None

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown(
            """
            <h2 style='margin-bottom:0.2rem; margin-top:0rem;'>
                📄 Texto Técnico (Abstract)
            </h2>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='margin-top:0rem; margin-bottom:0.3rem;'>Ingresa el resumen técnico aquí:</p>",
            unsafe_allow_html=True
        )

    with right_col:
        st.markdown(
            """
            <h2 style='margin-bottom:0.2rem; margin-top:0rem;'>
                ✨ Resumen Simplificado
            </h2>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='margin-top:0rem; margin-bottom:0.3rem;'>A continuación se presenta el resumen realizado:</p>",
            unsafe_allow_html=True
        )

    col1, col2 = st.columns([1, 1])

    # ---------------------------------------------------------
    # IZQUIERDA: INPUT + BOTONES
    # ---------------------------------------------------------
    with col1:
        input_text = st.text_area(
            "",
            height=240,
            placeholder="Ejemplo: The patient presented with acute myocardial infarction...",
            label_visibility="collapsed",
        )

        col_btn1, col_btn2 = st.columns([1, 1])

        with col_btn1:
            generate_btn = st.button(
                "Generar Resumen Sencillo",
                use_container_width=True,
                type="primary",
                help="Generar resumen en lenguaje sencillo",
                key="btn_generar",
            )

        with col_btn2:
            limpiar_btn = st.button(
                "Limpiar",
                use_container_width=True,
                help="Limpiar texto y resultado",
                key="btn_limpiar",
            )

        st.markdown(
            """
            <style>
                /* Botón generar - verde suave */
                div[data-testid="stButton"][key="btn_generar"] button {
                    background-color: #4CAF50 !important;
                    color: white !important;
                    border-radius: 8px !important;
                    border: 1px solid #3d8b41 !important;
                }
                div[data-testid="stButton"][key="btn_generar"] button:hover {
                    background-color: #45a049 !important;
                }

                /* Botón limpiar – amarillo suave */
                div[data-testid="stButton"][key="btn_limpiar"] button {
                    background-color: #f1c40f !important;
                    color: black !important;
                    border-radius: 8px !important;
                    border: 1px solid #d4ac0d !important;
                }
                div[data-testid="stButton"][key="btn_limpiar"] button:hover {
                    background-color:#d4ac0d !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        if limpiar_btn:
            st.session_state["texto_resumen"] = ""
            st.session_state["metricas"] = None
            st.session_state["metricas_clasificacion"] = None

    # ---------------------------------------------------------
    # DERECHA: RESUMEN
    # ---------------------------------------------------------
    with col2:
        resumen_box = st.empty()

        if not st.session_state.get("texto_resumen"):
            resumen_box.markdown(
                """
                <div style="
                    border:1px solid #113355;
                    padding:1rem;
                    border-radius:8px;
                    background-color:#0b1e33;
                    color:#d0d0d0;
                ">
                    Aquí aparecerá el resumen simplificado generado a partir del texto técnico.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---------------------------------------------------------
    # PROCESAMIENTO (CLASIFICACIÓN + RESUMEN)
    # ---------------------------------------------------------
    if generate_btn and input_text.strip():
        with st.spinner("Generando resumen..."):
            # 1) Clasificación del texto
            clasificacion = classify_text(input_text)

            # 2) Resumen
            data, error = call_local_model(input_text)

        if error:
            st.error(error)
        else:
            st.session_state["texto_resumen"] = data["summary"]

            # guardar métricas resumen
            st.session_state["metricas"] = {
                "legibilidad": f"{data['readability']*100:.1f}%",
                "factibilidad": f"{data['factuality']*100:.1f}%",
                "accuracy": f"{data['accuracy']*100:.1f}",
            }

            # guardar métricas clasificación
            st.session_state["metricas_clasificacion"] = {
                "label": clasificacion["label"],
                "precision": f"{clasificacion['precision']*100:.1f}%",
                "recall": f"{clasificacion['recall']*100:.1f}%",
                "f1": f"{clasificacion['f1']*100:.1f}%"
            }

    # ---------------------------------------------------------
    # MOSTRAR RESUMEN
    # ---------------------------------------------------------
    if st.session_state.get("texto_resumen"):
        resumen_box.markdown(
            f"""
            <div style="
                border:1px solid #444;
                padding:1rem;
                border-radius:8px;
                background-color:#1e1e1e;
                font-size:15px;
                color:#e0e0e0;
            ">{st.session_state['texto_resumen']}</div>
            """,
            unsafe_allow_html=True
        )

    # ---------------------------------------------------------
    # MÉTRICAS DE CLASIFICACIÓN (BLOQUE NUEVO)
    # ---------------------------------------------------------
    metricas_clf = st.session_state.get("metricas_clasificacion")

    if metricas_clf:
        st.markdown(
            """
            <h3 style='margin-top:2rem; margin-bottom:0.5rem; text-align:center;'>
                🧪 Métricas – Clasificación del Texto Original
            </h3>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Tipo de texto", metricas_clf["label"])
        c2.metric("Precision", metricas_clf["precision"])
        c3.metric("Recall", metricas_clf["recall"])
        c4.metric("F1-score", metricas_clf["f1"])

    # ---------------------------------------------------------
    # MÉTRICAS DE GENERACIÓN (TU BLOQUE ORIGINAL)
    # ---------------------------------------------------------
    metricas = st.session_state.get("metricas")

    if metricas:
        st.markdown("<div style='margin-top:0.8rem; margin-bottom:0.2rem;'></div>", unsafe_allow_html=True)

        metrics_center = st.container()

        with metrics_center:
            mcol1, mcol2, mcol3 = st.columns([1, 1, 1], gap="small")

            with mcol1:
                st.metric("📘 Legibilidad", metricas["legibilidad"])

            with mcol2:
                st.metric("🔍 Factibilidad", metricas["factibilidad"])

            with mcol3:
                st.metric("🎯 Accuracy", metricas["accuracy"] + "%")