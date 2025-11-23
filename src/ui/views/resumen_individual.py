import streamlit as st
from services import call_api, call_api_summary, call_api_metrics


def limpiar_estado():
    st.session_state["input_text"] = ""
    st.session_state["texto_resumen"] = ""
    st.session_state["metricas"] = None
    st.session_state["metricas_clasificacion"] = None


def render():

        #Inicializar estado
        if "input_text" not in st.session_state:
            st.session_state["input_text"] = ""

        if "texto_resumen" not in st.session_state:
            st.session_state["texto_resumen"] = ""

        if "metricas" not in st.session_state:
            st.session_state["metricas"] = None

        if "metricas_clasificacion" not in st.session_state:
            st.session_state["metricas_clasificacion"] = None

        #Encabezados izquierda y derecha

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

        #Area de texto + botones

        col1, col2 = st.columns([1, 1])

        with col1:

            input_text = st.text_area(
                "",
                height=240,
                placeholder="Ejemplo: The patient presented with acute myocardial infarction...",
                label_visibility="collapsed",
                key="input_text"
            )

            col_btn1, col_btn2 = st.columns([1, 1])

            with col_btn1:
                generate_btn = st.button(
                    "Generar Resumen Sencillo",
                    use_container_width=True,
                    type="primary",
                    help="Generar resumen en lenguaje sencillo",
                    key="btn_generar"
                )

            with col_btn2:
                limpiar_btn = st.button(
                    "Limpiar",
                    use_container_width=True,
                    help="Limpiar texto y resultado",
                    key="btn_limpiar",
                    on_click=limpiar_estado
                )

            #Estilos de botones
            st.markdown(
                """
                <style>
                    div[data-testid="stButton"][key="btn_generar"] button {
                        background-color: #4CAF50 !important;
                        color: white !important;
                        border-radius: 8px !important;
                        border: 1px solid #3d8b41 !important;
                    }
                    div[data-testid="stButton"][key="btn_generar"] button:hover {
                        background-color: #45a049 !important;
                    }

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

        #Cuadro de resultado (lado derecho)

        with col2:
            resumen_box = st.empty()

            if not st.session_state["texto_resumen"]:
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

        #Procesamiento principal

        if generate_btn and input_text.strip():

            with st.spinner("Generando resumen..."):

                clasificacion, error_clf = call_api(input_text)

                if error_clf:
                    st.error(error_clf)
                    return

                label = clasificacion["classification"]["label"]

                #Caso NO científico
                if label == "No científico":

                    mensaje_no_cient = (
                        "⚠️ El texto ingresado no es científico. "
                        "Por favor ingresa un abstract o texto técnico válido."
                    )

                    st.session_state["texto_resumen"] = mensaje_no_cient

                    resumen_box.markdown(
                        f"""
                        <div style="
                            border:1px solid #551111;
                            padding:1rem;
                            border-radius:8px;
                            background-color:#2a0d0d;
                            font-size:15px;
                            color:#ffdddd;
                        ">{mensaje_no_cient}</div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.session_state["metricas"] = None
                    st.session_state["metricas_clasificacion"] = {
                        "label": "No científico",
                        "confidence": f"{clasificacion['classification']['confidence']*100:.1f}%"
                    }

                #Casi cientifico:
                else:

                    resumen, error_res = call_api_summary(input_text)

                    if error_res:
                        st.error(error_res)
                        return

                    st.session_state["texto_resumen"] = resumen

                    #Llamar API Metrics
                    metricas_real, error_m = call_api_metrics(input_text, resumen)

                    if error_m:
                        st.error("Error al calcular métricas: " + error_m)
                        st.session_state["metricas"] = None
                    else:
                        st.session_state["metricas"] = metricas_real

                    st.session_state["metricas_clasificacion"] = {
                        "label": label,
                        "confidence": f"{clasificacion['classification']['confidence']*100:.1f}%"
                    }

        #Mostrar resumen
        if st.session_state["texto_resumen"]:
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

        #Metricas de clasificacion

        metricas_clf = st.session_state["metricas_clasificacion"]

        if metricas_clf:
            st.markdown(
                """
                <h3 style='margin-top:2rem; margin-bottom:0.5rem; text-align:center;'>
                    🧪 Métricas – Clasificación del Texto Original
                </h3>
                """,
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)
            c1.metric("Tipo de texto", metricas_clf["label"])
            c2.metric("Confiabilidad", metricas_clf["confidence"])

        #Metricas del resumen

        metricas = st.session_state["metricas"]

        if metricas:

            st.markdown(
                """
                <h3 style='margin-top:2rem; margin-bottom:1rem; text-align:center;'>
                    📊 Métricas del Resumen
                </h3>
                """,
                unsafe_allow_html=True,
            )

            #KPIs principales
            mcol1, mcol2, mcol3 = st.columns([1, 1, 1], gap="small")

            leg = metricas["legibilidad"].get("mean_flesch_reading_ease", 0)
            fac = metricas["factualidad"].get("mean_alignscore_bin", 0)
            acc = metricas["relevancia"].get("mean_f1", 0) * 100

            with mcol1:
                st.metric("📘 Legibilidad (Flesch)", f"{leg:.2f}")

            with mcol2:
                st.metric("🔍 Factualidad (AlignScore BIN)", f"{fac:.2f}")

            with mcol3:
                st.metric("🎯 Relevancia (F1)", f"{acc:.1f}%")

            st.markdown("<br>", unsafe_allow_html=True)

            #Relevancia
            with st.expander("🔵 Relevancia (BERTScore) – ver detalles"):
                relev = metricas["relevancia"]
                for k, v in relev.items():
                    st.write(f"**{k}**: {v:.4f}")

            #Legibilidad
            with st.expander("🟢 Legibilidad (TextStat) – ver detalles"):
                legib = metricas["legibilidad"]
                for k, v in legib.items():
                    if isinstance(v, float):
                        st.write(f"**{k}**: {v:.4f}")
                    else:
                        st.write(f"**{k}**: {v}")

            #Factualidad
            with st.expander("🟣 Factualidad (AlignScore) – ver detalles"):
                fact = metricas["factualidad"]
                for k, v in fact.items():
                    st.write(f"**{k}**: {v:.4f}")