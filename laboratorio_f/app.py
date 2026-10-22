"""Laboratorio F: la normalidad y la distribución F.

Ejecutar con:   streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="Laboratorio F: normalidad y distribución F", page_icon=":material/stacked_line_chart:",
                   layout="wide", initial_sidebar_state="expanded")

paginas = {
    "Laboratorio": [
        st.Page("paginas/inicio.py", title="Inicio", default=True),
        st.Page("paginas/fundamentos.py", title="Fundamentos (caps. 7 y 8)"),
    ],
    "Experimentos": [
        st.Page("paginas/constructor.py", title="1. Construye tu F"),
        st.Page("paginas/cadena.py", title="2. Dónde se rompe la cadena"),
        st.Page("paginas/promesas.py", title="3. ¿Se cumple lo que promete la F?"),
        st.Page("paginas/intervalo.py", title="4. El intervalo para σ₂²/σ₁²"),
        st.Page("paginas/mapa.py", title="5. Mapa de robustez"),
        st.Page("paginas/descubre.py", title="6. Experimentos guiados"),
    ],
    "Herramientas": [
        st.Page("paginas/calculadora.py", title="Calculadora y ejemplos del libro"),
        st.Page("paginas/correspondencia.py", title="Correspondencia con el libro"),
    ],
}

st.navigation(paginas).run()
