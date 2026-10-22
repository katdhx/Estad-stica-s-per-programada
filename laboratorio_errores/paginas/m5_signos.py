import numpy as np
import pandas as pd
import streamlit as st

from nucleo import binomial as bn
from nucleo import graficos as gr
from nucleo import signos as sg
from nucleo import ui
from nucleo.ui import ALFA, NAVY

ui.preparar()
ss = st.session_state
M0 = 0.0

ui.encabezado(
    "Extensión opcional · La prueba de signos",
    "El ejemplo de Jones usa una binomial. ¿Se puede usar esa misma binomial para probar algo sobre una población "
    "que no es normal? Sí: contando signos.",
    "Módulo opcional y separado. Usa solo la lógica binomial de la Sección 10.2; no reemplaza ningún módulo.")

st.header("La idea en tres pasos")
st.markdown(
    "Sean $X_1, \\dots, X_n$ independientes de una población **continua** con mediana $M$, y $H_0: M = m_0$.\n\n"
    "1. Si $H_0$ es cierta, por definición de mediana $P(X_i > m_0) = 1/2$ para cada $i$, **sea cual sea la forma "
    "de la población** (normal, asimétrica, con colas pesadas…). Con población continua, $P(X_i = m_0) = 0$.\n"
    "2. Cada observación es un ensayo de Bernoulli («cae por encima de $m_0$») con probabilidad $1/2$, y los "
    "ensayos son independientes.\n"
    "3. Entonces $Y = \\#\\{i : X_i > m_0\\} \\sim \\text{Binomial}(n, 1/2)$ bajo $H_0$.")
st.markdown(
    "Es la misma estructura del ejemplo de Jones con $p_0 = 0.5$: la región de rechazo y α se calculan con la "
    "binomial **exacta**, sin suponer normalidad. Lo que sí se supone: independencia y población continua (en datos "
    "reales con empates en $m_0$, esas observaciones se descartan y n baja).")

st.header("Compruébalo: α no depende de la población")
c1, c2 = st.columns([1, 2.3], gap="large")
with c1:
    st.selectbox("Población (todas con mediana m₀ = 0)", list(sg.POBLACIONES), key="s_pob")
    st.caption(sg.POBLACIONES[ss.s_pob])
    st.slider("n", 5, 60, key="s_n")
    st.number_input("α máximo", min_value=0.005, max_value=0.2, step=0.005, format="%.3f", key="s_alfa")
    st.radio("Alternativa", ("superior", "inferior"), key="s_cola", horizontal=True,
             format_func=lambda c: "Hₐ: M > m₀" if c == "superior" else "Hₐ: M < m₀")
    st.select_slider("Experimentos simulados", [2000, 5000, 20000, 50000], key="s_m")
n, alfa_max, cola = int(ss.s_n), float(ss.s_alfa), ss.s_cola
c = sg.umbral(n, alfa_max, cola)
a_exacto = bn.alfa(n, 0.5, c, cola)
filas = []
for pob in sg.POBLACIONES:
    tasa, _ = sg.tasa_rechazo(pob, n, M0, alfa_max, cola, int(ss.s_m), semilla=7)
    filas.append({"Población": pob, "α exacto (binomial)": a_exacto, "Frecuencia de rechazo simulada": tasa,
                  "Error MC": float(np.sqrt(a_exacto * (1 - a_exacto) / int(ss.s_m)))})
with c2:
    rr = f"y ≥ {c}" if cola == "superior" else f"y ≤ {c}"
    ui.cifras([("Región de rechazo", rr, f"Y ~ Binomial({n}, 0.5) bajo H₀", NAVY),
               ("α exacto", ui.fmt(a_exacto, 5), f"el mayor posible ≤ {alfa_max:g} (binomial discreta)", ALFA)])
    st.dataframe(pd.DataFrame(filas).style.format({"α exacto (binomial)": "{:.5f}", "Frecuencia de rechazo simulada": "{:.5f}",
                                                    "Error MC": "{:.5f}"}), hide_index=True, width="stretch")
    st.markdown("Las cuatro frecuencias quedan dentro del error Monte Carlo del mismo α exacto, incluso con la "
                "Cauchy, que ni siquiera tiene media. Por eso la prueba es **no paramétrica**: su α no depende de "
                "la forma de la población.")
    rng = np.random.default_rng(3)
    x = sg.generar(ss.s_pob, n, M0, rng)[0]
    st.plotly_chart(gr.muestra_signos(x, M0), width="stretch")
    st.caption(f"Una muestra de la población {ss.s_pob.lower()}: {int((x > M0).sum())} signos + de {n}.")

ui.caja("<b>Qué no hace esta extensión.</b> No compara poblaciones ni usa rangos: no es Mann–Whitney ni Wilcoxon. "
        "Solo muestra que la lógica binomial del Módulo 1 sirve, tal cual, para una prueba exacta sobre la mediana. "
        "Su costo: al usar solo los signos, con datos normales suele tener menos potencia que la prueba Z.")
