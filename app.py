"""Laboratorio de intervalos de confianza — punto de entrada.

Ejecutar con:   streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Laboratorio de intervalos de confianza",
    page_icon=":material/straighten:",
    layout="wide",
    initial_sidebar_state="expanded",
)

paginas = {
    "Laboratorio": [
        st.Page("paginas/inicio.py", title="Inicio", default=True),
        st.Page("paginas/fundamentos.py", title="Fundamentos (caps. 7 y 8)"),
    ],
    "Experimentos": [
        st.Page("paginas/exp1_construccion.py", title="1. Construcción de intervalos"),
        st.Page("paginas/exp2_tamano.py", title="2. Tamaño muestral"),
        st.Page("paginas/exp3_cobertura.py", title="3. Cobertura"),
        st.Page("paginas/exp4_nivel.py", title="4. Nivel de confianza"),
        st.Page("paginas/exp5_distribuciones.py", title="5. Distribuciones muestrales"),
        st.Page("paginas/exp6_supuestos.py", title="6. Supuestos"),
    ],
    "Herramientas": [
        st.Page("paginas/calculadora.py", title="Calculadora y ejemplos del libro"),
        st.Page("paginas/correspondencia.py", title="Correspondencia con el libro"),
    ],
}

st.navigation(paginas).run()
