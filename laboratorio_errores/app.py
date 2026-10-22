"""El costo de equivocarse: errores tipo I y tipo II.

Laboratorio interactivo para las secciones 10.1, 10.2 y 10.4 de Wackerly, Mendenhall y
Scheaffer, «Estadística matemática con aplicaciones», 7.ª edición.

Ejecutar con:   streamlit run app.py
"""

import streamlit as st

from nucleo import estado

st.set_page_config(page_title="El costo de equivocarse: errores tipo I y II", page_icon=":material/balance:",
                   layout="wide", initial_sidebar_state="expanded")

estado.inicializar()
estado.conservar()

paginas = {
    "Laboratorio": [
        st.Page("paginas/inicio.py", title="Inicio: elementos de una prueba", default=True),
    ],
    "Módulos": [
        st.Page("paginas/m1_binomial.py", title="1. El ejemplo de Jones"),
        st.Page("paginas/m2_dilema.py", title="2. El dilema entre α y β"),
        st.Page("paginas/m3_montecarlo.py", title="3. Experimento Monte Carlo"),
        st.Page("paginas/m4_decision.py", title="4. Toma una decisión"),
    ],
    "Extensiones": [
        st.Page("paginas/excel.py", title="Excel: compruébalo y trae tus datos"),
        st.Page("paginas/m5_signos.py", title="Opcional: prueba de signos"),
    ],
}

st.navigation(paginas).run()
