import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from nucleo import fdist, graficos as gr
from nucleo import motor, teoria, ui
from nucleo.poblaciones import FORMAS, Poblacion, forma

P = "pro"
ui.preparar()
ui.encabezado(
    "3. ¿Se cumple lo que promete la F?",
    "La F permite calcular probabilidades sobre el cociente de dos varianzas muestrales, como en el Ejemplo 7.7 y el "
    "Ejercicio 7.27. Aquí se calculan esas mismas probabilidades con la F y con la simulación, y se ve cuánto se equivoca "
    "la F cuando las poblaciones no son normales.",
    "Ejemplo 7.7 (p. 363), Ejercicio 7.27 (p. 367), Definición 7.3 (p. 362).",
)

st.sidebar.header("Escenario")
st.sidebar.caption("Las dos poblaciones tienen la misma forma y la misma varianza, como en el Ejemplo 7.7.")
f = ui.selector_forma(f"{P}_f", "Forma de las dos poblaciones", "exponencial")
c1, c2 = st.sidebar.columns(2)
n1 = int(c1.number_input("n₁", 2, motor.N_MAX, 6, key=f"{P}_n1"))
n2 = int(c2.number_input("n₂", 2, motor.N_MAX, 10, key=f"{P}_n2"))
B = int(st.sidebar.number_input("Pares de muestras B", 1000, motor.B_MAX, 40000, 1000, key=f"{P}_B"))
esc = motor.Escenario(Poblacion(f), Poblacion(f), n1, n2, B, 2026)
ui.costo(esc)
bloq = ui.mostrar_errores(esc.validar())
if ui.boton(P, deshabilitado=bloq):
    b, av = ui.barra()
    r = ui.simular(esc, av)
    b.empty()
    ui.guardar(P, esc, r)

t_ej, t_n = st.tabs(["Las probabilidades del libro", "¿Mejora con más datos?"])

with t_ej:
    res, viejo = ui.recuperar(P, esc)
    if res is None:
        st.info("Pulsa «Ejecutar simulación». Los valores por defecto (n₁ = 6, n₂ = 10) son los del Ejemplo 7.7.")
    else:
        if viejo:
            ui.aviso_desactualizado()
        E = res.escenario
        g1, g2 = E.gl
        R = res.F_cociente
        ref = stats.f(g1, g2)
        F05 = fdist.f_critico(0.05, g1, g2)
        filas = [
            (f"P(S₁²/S₂² > F.05) = P(S₁²/S₂² > {F05:.3f})", "Ejemplo 7.7", 0.05, float(np.mean(R > F05))),
            ("P(S₁²/S₂² > 2)", "Ejercicio 7.27(a)", float(ref.sf(2)), float(np.mean(R > 2))),
            ("P(S₁²/S₂² < 0.5)", "Ejercicio 7.27(b)", float(ref.cdf(0.5)), float(np.mean(R < 0.5))),
            ("P(una varianza muestral ≥ el doble de la otra)", "Ejercicio 7.27(c)", float(ref.sf(2) + ref.cdf(0.5)),
             float(np.mean((R >= 2) | (R <= 0.5)))),
        ]
        df = pd.DataFrame(filas, columns=["Probabilidad", "Fuente", "Según la F", "Simulada"])
        df["Error estándar"] = np.sqrt(df["Simulada"] * (1 - df["Simulada"]) / E.B)
        df["Simulada / F"] = df["Simulada"] / df["Según la F"]
        st.dataframe(df.style.format({"Según la F": "{:.4f}", "Simulada": "{:.4f}", "Error estándar": "{:.4f}",
                                      "Simulada / F": "{:.2f}×"}), hide_index=True, use_container_width=True)
        ratio = df["Simulada / F"].iloc[0]
        if E.f_exacta:
            ui.veredicto(f"<b>La F acierta.</b> Con poblaciones normales, S₁²/S₂² sigue una F({g1}, {g2}) y las "
                         "probabilidades simuladas coinciden con las de la F dentro del error de simulación.", True)
        else:
            ui.veredicto(f"<b>La F se equivoca.</b> El evento que según la F ocurre el 5 % de las veces ocurre en realidad "
                         f"el {100 * df['Simulada'].iloc[0]:.1f} % ({ratio:.1f} veces más). Si usaras el Ejemplo 7.7 con "
                         f"estas poblaciones, subestimarías qué tan seguido una varianza muestral sale mucho mayor que la otra.",
                         False)
        st.markdown("**La distribución completa.** Línea negra: la F del libro. Barras azules: lo que pasó.")
        fig = gr.histograma_f(R, g1, g2, f"S₁²/S₂² con σ₁ = σ₂, n₁ = {E.n1}, n₂ = {E.n2}", region=(0, F05),
                              exacta=E.f_exacta, x="S₁²/S₂²", etiqueta_region="5 % superior según la F (Ejemplo 7.7)")
        ui.figura(fig, "promesas_hist", f"{P}_h")

with t_n:
    st.markdown("Cada curva es la probabilidad **real** de que S₁²/S₂² supere F.05 cuando n₁ = n₂ = n. La F promete 5 % "
                "para todo n. Las líneas discontinuas son los límites para n muy grande (complementario).")
    opciones = ["normal", "uniforme", "t", "exponencial", "gamma", "lognormal"]
    elegidas = st.multiselect("Formas a comparar (hasta 3)", opciones, default=["normal", "t", "exponencial"],
                              format_func=lambda k: FORMAS[k].nombre, key=f"{P}_formas", max_selections=3)
    cA, cB = st.columns([3, 1])
    ns = cA.multiselect("Valores de n", [5, 10, 20, 50, 100, 300, 1000], default=[5, 10, 20, 50, 100, 300, 1000], key=f"{P}_ns")
    Bn = int(cB.number_input("B por cada n", 500, 50000, 6000, 500, key=f"{P}_Bn"))
    if st.button("Calcular las curvas", type="primary", key=f"{P}_curvas", disabled=not (elegidas and ns)):
        b, av = ui.barra("Simulando cada forma y cada n…")
        series, lims = [], []
        for i, clave in enumerate(elegidas):
            fo = forma(clave)
            sub = lambda fr, i=i: av((i + fr) / len(elegidas))
            df = ui.cacheado(("pro_n", fo, tuple(sorted(ns)), Bn),
                             lambda fo=fo, sub=sub: motor.barrido_n(fo, fo, sorted(ns), Bn, 0.10, 2026, progreso=sub))
            d = df.rename(columns={"cola_sup": "prob"})
            d["ee"] = np.sqrt(d["prob"] * (1 - d["prob"]) / Bn)
            series.append((fo.nombre_corto(), d))
            lims.append((fo.nombre_corto(), teoria.cola_superior_limite(fo.curtosis(), 0.05)))
        b.empty()
        st.session_state[f"{P}_curvas_res"] = (series, lims, Bn)
    if f"{P}_curvas_res" in st.session_state:
        series, lims, Bn = st.session_state[f"{P}_curvas_res"]
        fig = go.Figure()
        for i, (nombre, d) in enumerate(series):
            col = gr.SERIES[i % 3]
            fig.add_trace(go.Scatter(x=d["n1"], y=d["prob"], mode="lines+markers", name=nombre,
                                     line=dict(color=col, width=2.4), marker=dict(size=9, color=col,
                                     symbol=("circle", "diamond", "square")[i % 3], line=dict(color="white", width=1.4)),
                                     error_y=dict(type="data", array=1.96 * d["ee"], color=col, thickness=1)))
            fig.add_hline(y=lims[i][1], line=dict(color=col, width=1.1, dash="dash"))
        fig.add_hline(y=0.05, line=dict(color=gr.TINTA, width=1.4, dash="dot"), annotation_text="lo que promete la F: 5 %",
                      annotation_position="bottom right")
        gr.base(fig, "P(S₁²/S₂² > F.05) según n", 440, x="n₁ = n₂ (escala logarítmica)", y="Probabilidad real")
        fig.update_xaxes(type="log")
        fig.update_yaxes(rangemode="tozero")
        ui.figura(fig, "promesas_vs_n", f"{P}_vn")
        ui.veredicto("<b>El patrón.</b> Con la normal la probabilidad se queda en 5 % para todo n. Con colas pesadas sube por "
                     "encima y <b>se estanca</b> en un valor mayor; no regresa al 5 %. Con colas livianas queda por debajo. "
                     "Más datos no corrigen un supuesto falso: el error está en la forma de la distribución, no en el tamaño "
                     "de la muestra.")
