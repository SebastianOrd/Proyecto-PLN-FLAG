import streamlit as st
st.set_option('deprecation.showPyplotGlobalUse', False)
from services import call_api, call_api_metrics, call_api_summary_stream,call_api_metrics_stream
from storage import log_run   
import matplotlib.pyplot as plt  
import io

def limpiar_estado():
    st.session_state["input_text"] = ""
    st.session_state["texto_resumen"] = ""
    st.session_state["metricas"] = None
    st.session_state["metricas_clasificacion"] = None
    
def make_fre_figure(fre_value: float):
    fig, ax = plt.subplots(figsize=(4, 2.2))

    ax.bar(["FRE"], [fre_value], color="#4CAF50", width=0.5)

    ax.axhline(60, color="red", linestyle="--", linewidth=2, zorder=5)
    ax.axhline(30, color="red", linestyle="--", linewidth=2, zorder=5)

    ax.set_ylabel("Flesch Reading Ease")
    ax.set_ylim(0, 100)
    ax.set_title("Legibilidad – Flesch Reading Ease", color="white")

    # Estética oscura
    fig.patch.set_facecolor("#1e1e1e")
    ax.set_facecolor("#1e1e1e")
    ax.tick_params(colors="white")
    ax.yaxis.label.set_color("white")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("white")
    ax.spines["bottom"].set_color("white")

    return fig
    
def make_text_standard_figure(text_standard_value: float):
    fig, ax = plt.subplots(figsize=(5, 2.5))

    ax.bar(["Text Standard"], [text_standard_value], color="#1f77b4", width=0.5)

    ax.axhline(10, color="red", linestyle="--", linewidth=2, zorder=5)
    ax.axhline(7, color="red", linestyle="--", linewidth=2, zorder=5)

    ax.set_ylabel("Grado escolar estimado")
    ax.set_ylim(0, max(12, text_standard_value + 2))
    ax.set_title("Legibilidad – Text Standard", color="white")

    # Estética oscura
    fig.patch.set_facecolor("#1e1e1e")
    ax.set_facecolor("#1e1e1e")
    ax.tick_params(colors="white")
    ax.yaxis.label.set_color("white")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("white")
    ax.spines["bottom"].set_color("white")

    return fig


def render():

    # Inicializar estado
    if "input_text" not in st.session_state:
        st.session_state["input_text"] = ""

    if "texto_resumen" not in st.session_state:
        st.session_state["texto_resumen"] = ""

    if "metricas" not in st.session_state:
        st.session_state["metricas"] = None

    if "metricas_clasificacion" not in st.session_state:
        st.session_state["metricas_clasificacion"] = None

    # Encabezados izquierda y derecha
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

    # Área de texto + botones
    col1, col2 = st.columns([1, 1])

    # ---------- BLOQUE IZQUIERDO: INPUT Y BOTONES ----------
    with col1:
        input_text = st.text_area(
            "",
            height=240,
            placeholder="Ejemplo: The patient presented with acute myocardial infarction...",
            label_visibility="collapsed",
            key="input_text"
        )

        # Tres botones: normal, streaming y limpiar
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

        with col_btn1:
            generate_btn = st.button(
                "Generar resumen",
                use_container_width=True,
                type="primary",
                help="Generar resumen en modo normal (con métricas)",
                key="btn_generar_normal",
            )
        with col_btn2:
            limpiar_btn = st.button(
                "Limpiar",
                use_container_width=True,
                help="Limpiar texto y resultado",
                key="btn_limpiar",
                on_click=limpiar_estado,
            )
        # Estilos de botones
        st.markdown(
            """
            <style>
                div[data-testid="stButton"][key="btn_generar_normal"] button {
                    background-color: #4CAF50 !important;
                    color: white !important;
                    border-radius: 8px !important;
                    border: 1px solid #3d8b41 !important;
                }
                div[data-testid="stButton"][key="btn_generar_normal"] button:hover {
                    background-color: #45a049 !important;
                }

                div[data-testid="stButton"][key="btn_generar_stream"] button {
                    background-color: #2e86de !important;
                    color: white !important;
                    border-radius: 8px !important;
                    border: 1px solid #1b4f72 !important;
                }
                div[data-testid="stButton"][key="btn_generar_stream"] button:hover {
                    background-color:#21618c !important;
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

    # ---------- BLOQUE DERECHO: RESUMEN ----------
    with col2:
        resumen_box = st.empty()

        if st.session_state["texto_resumen"]:
            # Si ya tengo un resumen guardado, lo muestro SIEMPRE
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
                unsafe_allow_html=True,
            )
        else:
            # Solo si NO hay resumen previo, muestro el texto “vacío”
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
        st.markdown("<br>", unsafe_allow_html=True)
        metrics_btn = st.button(
            "Calcular métricas del resumen",
            use_container_width=True,
            help="Calcular legibilidad, relevancia y factualidad del resumen actual",
            key="btn_calcular_metricas",
        )    
    # Placeholders para métricas (clasificación y resumen) que iremos llenando por etapas
    metricas_clf_container = st.container()
    metricas_resumen_container = st.container()

    # ---------- PROCESAMIENTO PRINCIPAL (por etapas) ----------
    if generate_btn and input_text.strip():

        # 1) CLASIFICACIÓN
        with st.spinner("Clasificando texto (científico vs no científico)..."):
            clasificacion, error_clf = call_api(input_text)

        if error_clf:
            st.error(error_clf)
            return

        label = clasificacion["classification"]["label"]
        st.session_state["metricas_clasificacion"] = {
            "label": label,
            "confidence": f"{clasificacion['classification']['confidence']*100:.1f}%"
        }

        # Mostrar métricas de clasificación APENAS terminamos la primera API
        with metricas_clf_container:
            st.markdown(
                """
                <h3 style='margin-top:2rem; margin-bottom:0.5rem; text-align:center;'>
                    🧪 Métricas – Clasificación del Texto Original
                </h3>
                """,
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns(2)
            c1.metric("Tipo de texto", st.session_state["metricas_clasificacion"]["label"])
            c2.metric("Confiabilidad", st.session_state["metricas_clasificacion"]["confidence"])

        # Caso NO científico: detenemos flujo aquí
        if label == "No científico":
            mensaje_no_cient = (
                "⚠️ El texto ingresado no es científico. "
                "Por favor ingresa un abstract o texto técnico válido."
            )

            st.session_state["texto_resumen"] = mensaje_no_cient
            st.session_state["metricas"] = None

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
            # No seguimos a resumen ni métricas
            return

        # 2) RESUMEN (solo si es científico)
        resumen = render_resumen_stream(input_text, resumen_box)
        st.session_state["texto_resumen"] = resumen
        
        # Actualizamos inmediatamente el cuadro de resumen
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
    if metrics_btn:
        # Validar que ya exista resumen
        if not st.session_state.get("texto_resumen"):
            st.warning("Primero genera un resumen antes de calcular métricas.")
            return
    
        original = st.session_state.get("input_text", "").strip()
        resumen = st.session_state.get("texto_resumen", "").strip()
    
        if not original or not resumen:
            st.warning("No hay texto original o resumen para calcular métricas.")
            return
        # 3) MÉTRICAS DEL RESUMEN (STREAMING)
        st.markdown(
            """
            <h3 style='margin-top:2rem; margin-bottom:1rem; text-align:center;'>
                📊 Métricas del Resumen
            </h3>
            """,
            unsafe_allow_html=True,
        )

        # Placeholders para cada bloque
        leg_col, rel_col, fac_col = st.columns([1, 1, 1], gap="small")

        # Diccionario donde iremos acumulando
        metricas_acumuladas = {
            "legibilidad": None,
            "relevancia": None,
            "factualidad": None,
        }

        with st.spinner("Calculando métricas del resumen..."):
            try:
                for event in call_api_metrics_stream(input_text, resumen):
                    tipo = event.get("type")
                    data = event.get("data", {})
            
                    if tipo == "legibilidad":
                        # guardar TODO el diccionario
                        metricas_acumuladas["legibilidad"] = data
            
                        fre = float(data.get("mean_flesch_reading_ease", 0.0))
                        with leg_col:
                            st.metric("📘 Legibilidad (Flesch)", f"{fre:.2f}")
            
                    elif tipo == "relevancia":
                        metricas_acumuladas["relevancia"] = data
                        f1 = data.get("mean_f1", 0.0) * 100
                        with rel_col:
                            st.metric("🎯 Relevancia (F1)", f"{f1:.1f}%")
            
                    elif tipo == "factualidad":
                        metricas_acumuladas["factualidad"] = data
                        score = data.get("mean_alignscore_nli", 0.0)
                        with fac_col:
                            st.metric("🔍 Factualidad", f"{score:.2f}")

                    elif tipo == "done":
                        break
            except RuntimeError as e:
                st.warning(str(e))
                return
            except Exception as e:
                st.error(f"Error inesperado al calcular métricas: {e}")
                return      
        # Guardamos en session_state por si luego quieres usar expanders
        st.session_state["metricas"] = metricas_acumuladas
        
        metricas = st.session_state["metricas"]

        # Si quieres seguir teniendo los expanders de detalle:
        # ------- Legibilidad: detalles + gráficas -------
        leg_raw = metricas.get("legibilidad")
        
        if leg_raw:
            # Por si algún día leg_raw llegara como float, lo normalizamos
            if isinstance(leg_raw, (int, float)):
                leg = {"mean_flesch_reading_ease": float(leg_raw)}
            else:
                leg = leg_raw
        
            fre = float(leg.get("mean_flesch_reading_ease", 0.0))
            text_std = float(leg.get("mean_flesch_kincaid_grade", 0.0))
        
            with st.expander("🟢 Legibilidad – detalles"):
                # Texto con todas las métricas
                for k, v in leg.items():
                    st.write(f"**{k}**: {v}")
        
                st.markdown("---")
                st.markdown("#### Gráficos de legibilidad")
        
                col_g1, col_g2 = st.columns(2)
        
                with col_g1:
                    st.markdown("**Flesch Reading Ease**")
                    fig_fre = make_fre_figure(fre)
                    st.pyplot(fig_fre)
        
                with col_g2:
                    st.markdown("**Flesch-Kincaid Grade**")
                    fig_std = make_text_standard_figure(text_std)
                    st.pyplot(fig_std)

        # Relevancia detallada
        if metricas["relevancia"]:
            with st.expander("🔵 Relevancia – detalles"):
                for k, v in metricas["relevancia"].items():
                    st.write(f"**{k}**: {v}")

        # Factualidad detallada
        if metricas["factualidad"]:
            with st.expander("🟣 Factualidad – detalles"):
                for k, v in metricas["factualidad"].items():
                    st.write(f"**{k}**: {v}")
        # -------------------------------------------------
        # Registrar el run en la "mini base de datos" local
        # -------------------------------------------------
        try:
            clf = st.session_state.get("metricas_clasificacion") or {}
            log_run(
                {
                    "timestamp": None,  # se rellena dentro de log_run
                    "original_text": input_text,
                    "summary_text": resumen,
                    "classification_label": clf.get("label"),
                    # mejor guardar la confianza como float, no como string "100.0%"
                    "classification_confidence": clf.get("confidence"),
                    "metrics_legibilidad": metricas.get("legibilidad"),
                    "metrics_relevancia": metricas.get("relevancia"),
                    "metrics_factualidad": metricas.get("factualidad"),
                }
            )
        except Exception as e:
            print(f"[UI] Error al guardar run en log: {e}")       
def render_resumen_stream(input_text: str, resumen_box=None) -> str:
    st.subheader("Resumen PLS (streaming)")
    buffer = ""
    if resumen_box is None:
        resumen_box = st.empty()
    with st.spinner("Generando resumen en tiempo real..."):
        try:
            for piece in call_api_summary_stream(input_text):
                if not piece:
                    continue
                # Si llega el marcador de fin, cortamos el bucle
                if "<<END_OF_SUMMARY_STREAM>>" in piece:
                    piece = piece.replace("<<END_OF_SUMMARY_STREAM>>", "")
                    buffer += piece
                    break
    
                buffer += piece
                resumen_box.markdown(
                f"""
                <div style="
                    border:1px solid #444;
                    padding:1rem;
                    border-radius:8px;
                    background-color:#1e1e1e;
                    font-size:15px;
                    color:#e0e0e0;
                ">{buffer}</div>
                """,
                unsafe_allow_html=True,
                )
        except RuntimeError as e:
            # Aquí capturas el error 429 enviado por el backend
            st.warning(str(e))
            return ""
    # Al terminar el streaming, mostramos el texto final
    resumen_box.markdown(
        f"""
        <div style="
            border:1px solid #444;
            padding:1rem;
            border-radius:8px;
            background-color:#1e1e1e;
            font-size:15px;
            color:#e0e0e0;
        ">{buffer}</div>
        """,
        unsafe_allow_html=True,
    )

    return buffer
