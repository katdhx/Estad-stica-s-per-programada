import re

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from nucleo import fdist, ui
from nucleo.ejemplos import EJEMPLOS

P = "cal"
ui.preparar()
ui.encabezado(
    "Calculadora y ejemplos del libro",
    "Resuelve paso a paso los ejemplos y ejercicios del libro sobre la F, o calcula con tus propios datos. Todo con la "
    "teoría normal, es decir, lo que sería exacto si las poblaciones fueran normales.",
    "Ejemplo 7.7 (p. 363), Ejercicios 7.27 (p. 367), 7.36 (p. 368), 8.125 y 8.126 (p. 441).",
)

t_ej, t_prob, t_ic = st.tabs(["Ejemplos del libro", "Probabilidades y cuantiles de S₁²/S₂²", "Intervalo con mis datos"])

with t_ej:
    clave = st.selectbox("Ejemplo", list(EJEMPLOS), format_func=lambda k: EJEMPLOS[k].titulo, key=f"{P}_ej")
    ej = EJEMPLOS[clave]
    g1, g2 = ej.n1 - 1, ej.n2 - 1
    st.markdown(f"**Enunciado (p. {ej.pagina}).** {ej.enunciado}")
    if ej.tipo == "cuantil":
        Fa = fdist.f_critico(1 - ej.confianza, g1, g2)
        st.markdown("**Paso 1.** Por el Teorema 7.3 y la Definición 7.3, con poblaciones normales:")
        st.latex(rf"\frac{{S_1^2/\sigma_1^2}}{{S_2^2/\sigma_2^2}}\sim F({g1},\,{g2}).")
        st.markdown(rf"**Paso 2.** Como $\sigma_1^2/\sigma_2^2={ej.razon_var:g}$, se tiene $S_1^2/S_2^2={ej.razon_var:g}\cdot F$, con $F\sim F({g1},{g2})$.")
        st.markdown(rf"**Paso 3.** $P(S_1^2/S_2^2\le b)={ej.confianza:g}$ equivale a $P(F\le b/{ej.razon_var:g})={ej.confianza:g}$, "
                    rf"así que $b/{ej.razon_var:g}=F_{{{1 - ej.confianza:.2f}}}({g1},{g2})={Fa:.4f}$.")
        st.latex(rf"b={ej.razon_var:g}\times{Fa:.4f}={ej.razon_var * Fa:.4f}")
    elif ej.tipo == "probabilidad":
        ref = stats.f(g1, g2)
        st.markdown(rf"Con varianzas iguales, $S_1^2/S_2^2\sim F({g1},{g2})$ (Definición 7.3).")
        st.latex(rf"\text{{(a)}}\ P(S_1^2/S_2^2>2)={ref.sf(2):.4f}\qquad\text{{(b)}}\ P(S_1^2/S_2^2<0.5)={ref.cdf(0.5):.4f}")
        st.latex(rf"\text{{(c)}}\ P(S_1^2/S_2^2\ge2)+P(S_1^2/S_2^2\le0.5)={ref.sf(2) + ref.cdf(0.5):.4f}")
        st.markdown("En (c), «una varianza es al menos el doble de la otra» significa que el cociente es ≥ 2 o ≤ 0.5. "
                    "El Experimento 3 compara estos números con la simulación cuando las poblaciones no son normales.")
    else:
        a = fdist.f_critico(1 - (1 - ej.confianza) / 2, g1, g2)
        b = fdist.f_critico((1 - ej.confianza) / 2, g1, g2)
        r = ej.s2_2 / ej.s2_1
        st.markdown("**Paso 1.** Pivote del Ejercicio 8.125: $\\dfrac{\\sigma_2^2}{\\sigma_1^2}\\cdot\\dfrac{S_1^2}{S_2^2}\\sim F(n_1-1,n_2-1)$.")
        st.latex(rf"F_{{.975}}({g1},{g2})={a:.4f},\qquad F_{{.025}}({g1},{g2})={b:.4f}")
        st.latex(rf"\frac{{s_2^2}}{{s_1^2}}=\frac{{{ej.s2_2:g}}}{{{ej.s2_1:g}}}={r:.4f}")
        st.latex(rf"\frac{{\sigma_2^2}}{{\sigma_1^2}}\in[{r:.4f}\times{a:.4f},\ {r:.4f}\times{b:.4f}]=[{r * a:.4f},\ {r * b:.4f}]")
        contiene = r * a <= 1 <= r * b
        st.markdown(rf"Para $\sigma_1^2/\sigma_2^2$ se toman los recíprocos: $[{1 / (r * b):.4f},\ {1 / (r * a):.4f}]$. "
                    + ("El intervalo contiene el 1: con 10 envíos por proveedor, los datos no bastan para afirmar que las "
                       "varianzas sean distintas, aunque s₁² sea casi el triple de s₂²." if contiene else
                       "El intervalo no contiene el 1: los datos indican varianzas distintas."))
    ui.veredicto(f"<b>Libro:</b> {ej.resultado_libro} {ej.nota}")
    ui.nota("Todo esto supone normalidad. Si las poblaciones tienen colas pesadas, estas probabilidades y este intervalo "
            "dejan de ser correctos (Experimentos 3 y 4).")

with t_prob:
    c = st.columns(4)
    n1 = int(c[0].number_input("n₁", 2, 100000, 6, key=f"{P}_n1"))
    n2 = int(c[1].number_input("n₂", 2, 100000, 10, key=f"{P}_n2"))
    rv = float(c[2].number_input("σ₁²/σ₂²", 0.001, 1000.0, 1.0, key=f"{P}_rv"))
    b = float(c[3].number_input("b", 0.0001, 1000.0, 2.0, key=f"{P}_b"))
    g1, g2 = n1 - 1, n2 - 1
    ref = stats.f(g1, g2)
    st.latex(rf"P(S_1^2/S_2^2\le {b:g})=P\!\left(F\le \frac{{{b:g}}}{{{rv:g}}}\right)={ref.cdf(b / rv):.5f},\qquad "
             rf"P(S_1^2/S_2^2> {b:g})={ref.sf(b / rv):.5f}")
    tabla = pd.DataFrame({"a": [0.10, 0.05, 0.025, 0.01, 0.005]})
    tabla[f"F_a({g1}, {g2})"] = [fdist.f_critico(a, g1, g2) for a in tabla["a"]]
    tabla[f"F_(1−a)({g1}, {g2}) = 1/F_a({g2}, {g1})"] = [1 / fdist.f_critico(a, g2, g1) for a in tabla["a"]]
    st.dataframe(tabla.style.format({c: "{:.4f}" for c in tabla.columns}), hide_index=True, use_container_width=True)
    ui.nota("La segunda columna usa el Ejercicio 7.29: los cuantiles inferiores de la F son recíprocos de los superiores "
            "con los grados de libertad intercambiados.")

with t_ic:
    def leer(t: str) -> np.ndarray:
        partes = [p for p in re.split(r"[\s;,]+", t.strip()) if p]
        return np.array([float(p) for p in partes])
    try:
        y1 = leer(st.text_area("Muestra 1", "4.1 5.3 6.0 3.2 5.5 4.8 6.6 5.1 3.9 4.4", key=f"{P}_y1"))
        y2 = leer(st.text_area("Muestra 2", "5.0 5.2 4.9 5.4 5.1 4.7 5.3 5.0 4.8", key=f"{P}_y2"))
        conf = float(st.number_input("Confianza (%)", 50.0, 99.9, 95.0, 0.5, key=f"{P}_conf"))
        if y1.size < 2 or y2.size < 2:
            raise ValueError("Cada muestra necesita al menos 2 datos.")
        s1, s2 = y1.var(ddof=1), y2.var(ddof=1)
        L, U = fdist.intervalo_razon(s1, s2, y1.size, y2.size, 1 - conf / 100)
        st.latex(rf"n_1={y1.size},\ s_1^2={s1:.4f};\qquad n_2={y2.size},\ s_2^2={s2:.4f};\qquad s_2^2/s_1^2={s2 / s1:.4f}")
        st.latex(rf"\text{{IC del {conf:g}\%}}\ \text{{para}}\ \sigma_2^2/\sigma_1^2:\ [{float(L):.4f},\ {float(U):.4f}]")
        ui.veredicto("Este intervalo es exacto solo si las dos poblaciones son normales. Antes de confiar en él, mira la forma "
                     "de tus datos: si hay valores muy extremos (colas pesadas), su cobertura real puede ser mucho menor.")
    except ValueError as e:
        st.error(str(e) if "datos" in str(e) else "Escribe solo números separados por espacios o comas, con punto decimal.")
