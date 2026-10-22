import numpy as np
import pandas as pd
import streamlit as st

from nucleo import binomial as bn
from nucleo import estado
from nucleo import graficos as gr
from nucleo import montecarlo as mc
from nucleo import ui
from nucleo.ui import ALFA, BETA, POTENCIA

ui.preparar()
ss = st.session_state


def _al_cambiar_cola():
    # Reflejar p1 y el umbral para que sigan teniendo sentido con la nueva alternativa.
    ss.b_p1 = float(np.clip(round(2 * ss.b_p0 - ss.b_p1, 2), 0.01, 0.99))
    ss.b_c = int(ss.b_n - ss.b_c)   # y ≤ c  ↔  y ≥ n − c


def _caso_libro(c: int):
    ss.b_n, ss.b_p0, ss.b_p1, ss.b_c, ss.b_cola = 15, 0.5, 0.3, c, "inferior"


ui.encabezado(
    "Módulo 1 · El ejemplo de Jones",
    "Jones dice que ganará la elección. Se entrevista a n votantes y se cuenta Y, los que lo apoyan. "
    "Si Y sale muy pequeño, se rechaza que tenga la mitad de los votos. ¿Cuánto cuesta esa regla en errores?",
    "Sección 10.2: H₀: p = .5 contra Hₐ: p &lt; .5, Y ~ Binomial(15, p), RR = {y ≤ 2}; α en p = .5 y β en "
    "el valor específico p = .3. El libro compara además con la región RR = {y ≤ 5}.")

col_c, col_g = st.columns([1, 2.3], gap="large")
with col_c:
    st.subheader("Controles")
    st.slider("Tamaño de muestra n", 2, 100, key="b_n")
    st.slider("p₀ (bajo H₀)", 0.01, 0.99, step=0.01, key="b_p0")
    st.radio("Hipótesis alternativa", bn.COLAS, key="b_cola", horizontal=True, on_change=_al_cambiar_cola,
             format_func=lambda c: "Hₐ: p < p₀" if c == "inferior" else "Hₐ: p > p₀")
    st.slider("p₁ (un valor específico de Hₐ)", 0.01, 0.99, step=0.01, key="b_p1")
    n = int(ss.b_n)
    if ss.b_cola == "inferior":
        ss.b_c = int(np.clip(ss.b_c, 0, n))
        st.slider("Umbral c: rechazar H₀ si y ≤ c", 0, n, key="b_c")
    else:
        ss.b_c = int(np.clip(ss.b_c, 1, n))
        st.slider("Umbral c: rechazar H₀ si y ≥ c", 1, n, key="b_c")
    st.button("Caso del libro: RR = {y ≤ 2}", on_click=_caso_libro, args=(2,), width="stretch")
    st.button("Región que compara el libro: RR = {y ≤ 5}", on_click=_caso_libro, args=(5,), width="stretch")

ok, msg = estado.binom_valida()
if not ok:
    with col_g:
        st.error(msg)
    st.stop()

b = estado.binom()
n, p0, p1, c, cola = b["n"], b["p0"], b["p1"], b["c"], b["cola"]
a = bn.alfa(n, p0, c, cola)
be = bn.beta(n, p1, c, cola)
rr_txt = f"y ≤ {c}" if cola == "inferior" else f"y ≥ {c}"
nr_txt = f"y > {c}" if cola == "inferior" else f"y < {c}"

with col_g:
    ui.cifras([
        ("α = P(error tipo I)", ui.fmt(a, 5), f"P({rr_txt} | p = {p0:.2f})", ALFA),
        ("β(p₁) = P(error tipo II)", ui.fmt(be, 5), f"P({nr_txt} | p = {p1:.2f})", BETA),
        ("Potencia en p₁", ui.fmt(1 - be, 5), "1 − β(p₁)", POTENCIA),
    ])
    if (n, round(p0, 2), round(p1, 2), cola) == (15, 0.5, 0.3, "inferior") and c in (2, 5):
        ref = {2: "α ≈ .004 y β(.3) ≈ .873", 5: "α ≈ .151 y β(.3) ≈ .278"}[c]
        st.success(f"Coincide con el libro para RR = {{y ≤ {c}}}: {ref}.")
    st.plotly_chart(gr.binomiales(n, p0, p1, c, cola), width="stretch")

st.markdown(
    f"En la gráfica de la izquierda las barras rojas son los valores de Y con los que se rechaza **aunque H₀ sea "
    f"verdadera**: su suma es α. A la derecha, las azules son los valores con los que **no** se rechaza aunque "
    f"el verdadero p sea {p1:.2f}: su suma es β. Las verdes, su complemento, son la potencia.")
st.latex(rf"\alpha = \sum_{{y \in RR}} \binom{{{n}}}{{y}} ({p0:.2f})^y (1-{p0:.2f})^{{{n}-y}} = {a:.5f}"
         rf"\qquad \beta({p1:.2f}) = \sum_{{y \notin RR}} \binom{{{n}}}{{y}} ({p1:.2f})^y (1-{p1:.2f})^{{{n}-y}} = {be:.5f}")

st.header("Toda la alternativa, no solo p₁")
st.plotly_chart(gr.curva_beta(n, p0, p1, c, cola), width="stretch")
ui.caja(
    f"<b>p₁ = {p1:.2f} es un solo punto de Hₐ.</b> La hipótesis alternativa es compuesta "
    f"({'p &lt; ' if cola == 'inferior' else 'p &gt; '}{p0:.2f}), así que β cambia con el valor verdadero: "
    f"cerca de p₀ la prueba casi no distingue (β se acerca a 1 − α) y lejos de p₀ casi nunca falla. "
    "La parte punteada no es β: ahí H₀ (o algo que no está en Hₐ) es lo verdadero.")

st.header("Todas las reglas posibles con este n")
cs = range(0, n + 1) if cola == "inferior" else range(1, n + 1)
tabla = pd.DataFrame([{"Región de rechazo": f"y ≤ {k}" if cola == "inferior" else f"y ≥ {k}",
                       "α": bn.alfa(n, p0, k, cola), f"β({p1:.2f})": bn.beta(n, p1, k, cola),
                       f"Potencia en {p1:.2f}": bn.potencia(n, p1, k, cola), "_c": k} for k in cs])
estilo = (tabla.drop(columns="_c").style.format({"α": "{:.5f}", f"β({p1:.2f})": "{:.5f}", f"Potencia en {p1:.2f}": "{:.5f}"})
          .apply(lambda f: ["background-color: #E8EEF4; font-weight: 600" if tabla.loc[f.name, "_c"] == c else ""
                            for _ in f], axis=1))
st.dataframe(estilo, hide_index=True, width="stretch", height=min(38 * (len(tabla) + 1), 420))
st.markdown("Al bajar por la tabla la región crece: **α sube y β baja**. Con n fijo no hay una fila con los dos "
            "pequeños; para lograrlo hay que aumentar n (Módulo 2 y Sección 10.4).")

st.header("Comprobación por simulación")
st.select_slider("Número de simulaciones", [500, 1000, 5000, 10000, 50000, 100000], key="b_m")
m = int(ss.b_m)
rng = np.random.default_rng(15)
_, rech0 = bn.simular(n, p0, c, cola, m, rng)
_, rech1 = bn.simular(n, p1, c, cola, m, rng)
a_emp, b_emp = float(rech0.mean()), float(1 - rech1.mean())
ui.cifras([
    ("α empírico", ui.fmt(a_emp, 5), f"exacto {a:.5f} · error MC {mc.error_mc(a_emp, m):.5f}", ALFA),
    ("β empírico", ui.fmt(b_emp, 5), f"exacto {be:.5f} · error MC {mc.error_mc(b_emp, m):.5f}", BETA),
])
st.caption(f"Se repitió {m:,} veces el experimento bajo p₀ y otras {m:,} bajo p₁, con la misma regla. "
           "El Módulo 3 hace esto con todo detalle.".replace(",", "."))
