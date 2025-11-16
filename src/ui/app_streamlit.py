import streamlit as st

from views import resumen_individual, explorar_resultados


#Configuración general de la página
st.set_page_config(
    page_title="BioLaySumm",
    page_icon="🩺",
    layout="wide",
)


def render_header(section_title: str) -> None:
    """
    Encabezado principal reutilizable para cada sección.
    Ahora se muestra de forma similar al texto de st.set_page_config().
    """

    #ttulo
    st.markdown(
        """
        <h1 style="margin-bottom:0.1rem; margin-top:0.2rem; display:flex; align-items:center; gap:0.5rem;">
            🏥 <span>BioLaySumm: Resúmenes Médicos Simplificados</span>
        </h1>
        """,
        unsafe_allow_html=True,
    )

    #subtutulo descriptivo
    st.markdown(
        """
        <p style="margin-top:0rem; margin-bottom:0.6rem; color:#d0d0d0;">
            Plain Language Summaries for Health – Modelo DeepSeek con finetuning
            para la generación de resúmenes en lenguaje claro y sencillo para todas las personas.
        </p>
        """,
        unsafe_allow_html=True,
    )

    #título de la sección
    st.markdown(
        f"""
        <h2 style="margin-top:0.2rem; margin-bottom:0.5rem;">
            {section_title}
        </h2>
        """,
        unsafe_allow_html=True,
    )
#sidebar

st.sidebar.markdown(
    """
    <h3 style="margin-top:0.5rem; margin-bottom:0.2rem;">BioLaySumm</h3>
    <p style="font-size:0.9rem; color:#d0d0d0; margin-bottom:0.8rem;">
        Plain Language Summaries para textos clínicos y biomédicos.
    </p>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("### 📂 Secciones")
choice = st.sidebar.radio(
    "Navegación",
    ["Resumen individual", "Explorar resultados generados"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <p style="font-size:0.85rem; color:#bbbbbb;">
    Proyecto de grado – Generación automática de PLS en salud
    a partir de modelos de lenguaje finetuneados (&lt;3B parámetros).
    </p>
    """,
    unsafe_allow_html=True,
)

#rutas
if choice == "Resumen individual":
    render_header("Resumen individual")
    resumen_individual.render()

elif choice == "Explorar resultados generados":
    render_header("Explorar resultados generados")
    explorar_resultados.render()