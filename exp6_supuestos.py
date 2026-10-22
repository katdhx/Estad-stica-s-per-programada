import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from lab import graficos as gr
from lab import intervalos as ic
from lab import motor, teoria, ui
from lab.poblaciones import crear

P = "e6"
ui.preparar()
ui.encabezado(
    "Experimento 6. Supuestos",
    "Cada resultado exacto del capítulo 7 tiene hipótesis. ¿Qué pasa si se usan los intervalos cuando no se cumplen? "
    "Algunos procedimientos se recuperan al crecer n gracias al TCL; otros no se recuperan nunca.",
    "Secciones 8.8, 8.9 y 8.10 (p. 425–437), Sección 7.5 (regla p ± 3√(pq/n)), Ejercicios 8.54–8.55.",
)

st.sidebar.header("Simulación")
B = int(st.sidebar.number_input("Muestras B por escenario", 200, 50000, 3000, step=500, key=f"{P}_B"))
conf = st.sidebar.number_input("Nivel de confianza (%)", 50.0, 99.9, 95.0, 0.5, key=f"{P}_conf")
alfa = round(1 - conf / 100, 6)
semilla = int(st.sidebar.number_input("Semilla aleatoria", 0, 2**31 - 1, 2026, key=f"{P}_sem"))
ui.nota("Cada pestaña tiene su propio botón: las simulaciones solo se ejecutan cuando lo pulsas.")

POBS = {
    "Normal": crear("normal", mu=0, sigma=1),
    "Uniforme(0, 1)": crear("uniforme", a=0, b=1),
    "t con 5 gl": crear("t", nu=5),
    "Gamma(α = 4)": crear("gamma", alpha=4, beta=1),
    "Exponencial": crear("exponencial", theta=1),
    "Log-normal (s = 0.75)": crear("lognormal", m=0, s=0.75),
}

t_chi, t_t, t_p, t_pool, t_res = st.tabs([
    "χ² para σ² sin normalidad", "t para μ sin normalidad", "Proporción cerca de 0 o 1",
    "t agrupada con varianzas distintas", "Exacto frente a asintótico",
])


def barrido_poblaciones(proc: str, nombres: list[str], ns: list[int], clave: str):
    filas = []
    barra, avance = ui.barra_progreso("Simulando…")
    for i, nom in enumerate(nombres):
        esc = motor.Escenario(proc, POBS[nom], n1=ns[0], B=B, alfa=alfa, semilla=semilla + i)
        df = ui.barrido_cache(esc, tuple(ns))
        df["procedimiento"] = nom
        filas.append(df)
        avance((i + 1) / len(nombres))
    barra.empty()
    st.session_state[clave] = (proc, tuple(nombres), tuple(ns), B, alfa, pd.concat(filas, ignore_index=True))


# ======================================================================
with t_chi:
    st.markdown(
        "El intervalo $[(n-1)S^2/\\chi^2_{\\alpha/2},\\ (n-1)S^2/\\chi^2_{1-\\alpha/2}]$ descansa en el Teorema 7.3, que exige "
        "normalidad. La Sección 8.9 advierte que fuera de ella el coeficiente real «puede diferir en forma marcada». "
        "Aquí se mide cuánto."
    )
    nombres = st.multiselect("Poblaciones", list(POBS), default=["Normal", "Uniforme(0, 1)", "t con 5 gl", "Exponencial"],
                             key=f"{P}_chi_pobs")
    ns = st.multiselect("Valores de n", [5, 10, 20, 30, 50, 100, 300, 1000, 3000], default=[5, 10, 30, 100, 300, 1000],
                        key=f"{P}_chi_ns")
    if st.button("Simular el intervalo χ²", type="primary", key=f"{P}_chi_btn", disabled=not (nombres and ns)):
        barrido_poblaciones("varianza_chi2", nombres, sorted(ns), f"{P}_chi_res")
    if f"{P}_chi_res" in st.session_state:
        proc, noms, ns_, B_, a_, df = st.session_state[f"{P}_chi_res"]
        teo = {}
        filas = []
        for nom in noms:
            k = POBS[nom].curtosis_exceso()
            lim = teoria.cobertura_limite_chi2(k, a_)
            teo[nom] = (np.array(ns_), np.full(len(ns_), lim))
            ult = df[df["procedimiento"] == nom].iloc[-1]
            filas.append({"Población": nom, "Curtosis en exceso κ": k, f"Cobertura con n = {ns_[-1]}": ult["cobertura"],
                          "Límite cuando n → ∞": lim})
        fig = gr.curva_vs_n(df, "cobertura", {n: n for n in noms}, "Cobertura del intervalo χ² para σ²",
                            y="Cobertura", nominal=1 - a_, columna_error="ee_cobertura", B=B_)
        for i, nom in enumerate(noms):
            xs, ys = teo[nom]
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=gr.SERIES[i % 3], width=1, dash="dash"),
                                     name=f"Límite teórico: {nom}", hoverinfo="skip",
                                     showlegend=False))
        ui.mostrar_figura(fig, "experimento6_chi2", f"{P}_chi")
        st.dataframe(pd.DataFrame(filas).style.format({"Curtosis en exceso κ": "{:.3f}",
                                                        f"Cobertura con n = {ns_[-1]}": "{:.4f}",
                                                        "Límite cuando n → ∞": "{:.4f}"}),
                     hide_index=True, use_container_width=True)
        if len(noms) > 3:
            ui.nota("A partir de la cuarta población los colores se repiten; esas curvas usan trazo punteado y otro marcador.")
        ui.veredicto("<b>Conclusión.</b> Con colas más pesadas que la normal (κ > 0: t, exponencial, log-normal), la "
                     "cobertura queda por debajo de la nominal y <b>no mejora al crecer n</b>: converge a un valor "
                     "equivocado. Con colas más livianas (uniforme, κ < 0) el intervalo es conservador. Solo con κ = 0 "
                     "se obtiene el nivel nominal. El TCL no rescata este intervalo.")
        st.markdown(r"""
**Por qué (explicación complementaria, no está en el libro).** $S^2$ es un promedio de cuadrados, así que por el TCL
$(n-1)S^2/\sigma^2$ es aproximadamente normal con media $n-1$, pero con **varianza $(n-1)(2+\kappa)$**, donde
$\kappa=E[(Y-\mu)^4]/\sigma^4-3$. El intervalo χ² usa los cuantiles de una $\chi^2_{n-1}$, cuya varianza es $2(n-1)$:
solo coinciden si $\kappa=0$. Para $n$ grande:
$$P\big(\chi^2_{1-\alpha/2}\le W\le\chi^2_{\alpha/2}\big)\ \longrightarrow\ 2\Phi\!\left(z_{\alpha/2}\sqrt{\tfrac{2}{2+\kappa}}\right)-1 .$$
Con la exponencial ($\kappa=6$) y 95 % el límite es $2\Phi(0.98)-1\approx0.67$. Las líneas discontinuas de la gráfica son estos límites.
""")

# ======================================================================
with t_t:
    st.markdown("El intervalo t es exacto bajo normalidad (Sección 8.8). El libro afirma que es «bastante estable» ante "
                "desviaciones moderadas (Sección 8.10). Con poblaciones asimétricas se nota para n pequeño, pero el TCL lo "
                "corrige al crecer n.")
    nombres_t = st.multiselect("Poblaciones ", list(POBS), default=["Normal", "Exponencial", "Log-normal (s = 0.75)"],
                               key=f"{P}_t_pobs")
    ns_t = st.multiselect("Valores de n ", [3, 5, 10, 20, 30, 50, 100, 300, 1000], default=[3, 5, 10, 20, 50, 100, 300],
                          key=f"{P}_t_ns")
    if st.button("Simular el intervalo t", type="primary", key=f"{P}_t_btn", disabled=not (nombres_t and ns_t)):
        barrido_poblaciones("media_t", nombres_t, sorted(ns_t), f"{P}_t_res")
    if f"{P}_t_res" in st.session_state:
        proc, noms, ns_, B_, a_, df = st.session_state[f"{P}_t_res"]
        fig = gr.curva_vs_n(df, "cobertura", {n: n for n in noms}, "Cobertura del intervalo t para μ", y="Cobertura",
                            nominal=1 - a_, columna_error="ee_cobertura", B=B_)
        ui.mostrar_figura(fig, "experimento6_t", f"{P}_tt")
        ui.veredicto("<b>Conclusión.</b> A diferencia del intervalo χ², la cobertura del intervalo t sí <b>converge a la "
                     "nominal</b> con cualquier población de varianza finita: T = (Ȳ − μ)/(S/√n) es asintóticamente N(0, 1) "
                     "(TCL y S → σ), y t_{α/2, n−1} → z_{α/2}. La asimetría de la población solo afecta a n pequeño.")

# ======================================================================
with t_p:
    st.markdown(
        "El intervalo $\\hat p\\pm z_{\\alpha/2}\\sqrt{\\hat p\\hat q/n}$ depende de la aproximación normal de la Sección 7.5. "
        "Su cobertura **exacta** se puede calcular sin simular, sumando probabilidades binomiales: "
        "$C(p)=\\sum_{y=0}^{n}P(Y=y)\\,\\mathbf 1\\{p\\in IC(y)\\}$ (cálculo complementario)."
    )
    c1, c2 = st.columns([1, 3])
    n_p = int(c1.number_input("n", 2, 5000, 35, key=f"{P}_np"))
    simular_mc = c1.checkbox("Añadir puntos de Monte Carlo", True, key=f"{P}_pmc")
    ps = np.linspace(0.005, 0.995, 991)
    exacta = teoria.cobertura_exacta_wald_curva(n_p, ps, alfa)
    validos = [p for p in ps if teoria.regla_binomial(n_p, p)]
    zona = (min(validos), max(validos)) if validos else None
    mc = None
    if simular_mc:
        filas = []
        for i, pv in enumerate([0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]):
            esc = motor.Escenario("proporcion_wald", crear("bernoulli", p=pv), n1=n_p, B=B, alfa=alfa, semilla=semilla + i)
            r = ui.simular_cache(esc)
            cb = r.cobertura()
            filas.append({"p": pv, "cobertura": cb.estimada, "ee": cb.error_estandar})
        mc = pd.DataFrame(filas)
    with c2:
        fig = gr.curva_p(ps, exacta, 1 - alfa, mc, f"Cobertura del intervalo para p con n = {n_p}", zona)
        ui.mostrar_figura(fig, "experimento6_proporcion", f"{P}_p")
    ui.nota("La cobertura oscila porque p̂ solo toma n + 1 valores. Los puntos de Monte Carlo caen sobre la curva exacta: "
            "es una validación independiente del motor de simulación.")
    filas = []
    for nn in (10, 100):
        filas.append({"Escenario": f"p = .90, n = {nn}" + (" (Ejercicio 8.54)" if nn == 10 else " (Ejercicio 8.55)"),
                      "P(p̂ = 1) = .9ⁿ": 0.9**nn, "Cobertura exacta": teoria.cobertura_exacta_wald(nn, 0.9, alfa),
                      "¿Cumple p ± 3√(pq/n) ∈ (0, 1)?": "Sí" if teoria.regla_binomial(nn, 0.9) else "No"})
    st.dataframe(pd.DataFrame(filas).style.format({"P(p̂ = 1) = .9ⁿ": "{:.4f}", "Cobertura exacta": "{:.4f}"}),
                 hide_index=True, use_container_width=True)
    st.markdown("Con $p=.9$ y $n=10$, en el 35 % de las muestras sale $\\hat p=1$, el error estándar estimado es 0 y el "
                "intervalo es el punto $\\{1\\}$, que no contiene a $.9$. Esto **no invalida** el procedimiento (Ejercicio "
                "8.54e): simplemente se usó fuera de su condición de muestra grande.")

# ======================================================================
with t_pool:
    st.markdown("La t agrupada supone $\\sigma_1^2=\\sigma_2^2$. El libro dice que si $n_1\\approx n_2$ es robusta, pero que "
                "cuando $n_1$ y $n_2$ son muy distintos la suposición «se hace más importante» (p. 437). Ambas poblaciones son "
                "normales con $\\mu_1=\\mu_2$.")
    c1, c2, c3 = st.columns(3)
    razones = c1.multiselect("σ₂/σ₁", [1.0, 1.5, 2.0, 3.0, 4.0], default=[1.0, 2.0, 4.0], key=f"{P}_raz")
    disenos_txt = c2.multiselect("Diseños (n₁, n₂)", ["(10, 10)", "(30, 30)", "(10, 40)", "(40, 10)", "(5, 50)", "(50, 5)"],
                                 default=["(10, 10)", "(10, 40)", "(40, 10)"], key=f"{P}_dis")
    if c3.button("Simular", type="primary", key=f"{P}_pool_btn", disabled=not (razones and disenos_txt)):
        filas = []
        barra, avance = ui.barra_progreso()
        tot = len(razones) * len(disenos_txt)
        i = 0
        for r in razones:
            for d in disenos_txt:
                n1, n2 = (int(x) for x in d.strip("()").split(","))
                esc = motor.Escenario("dif_medias_t", crear("normal", mu=0, sigma=1), n1=n1, B=B, alfa=alfa,
                                      semilla=semilla + i, pob2=crear("normal", mu=0, sigma=r), n2=n2)
                res = ui.simular_cache(esc)
                cb = res.cobertura()
                sp2 = ((n1 - 1) + (n2 - 1) * r**2) / (n1 + n2 - 2)
                R = np.sqrt((1 / n1 + r**2 / n2) / (sp2 * (1 / n1 + 1 / n2)))
                aprox = 2 * stats.norm.cdf(ic.z_critico(alfa / 2) / R) - 1
                filas.append({"σ₂/σ₁": r, "diseño": d, "cobertura": cb.estimada, "ee": cb.error_estandar,
                              "aproximación (complementaria)": aprox})
                i += 1
                avance(i / tot)
        barra.empty()
        st.session_state[f"{P}_pool"] = pd.DataFrame(filas)
    if f"{P}_pool" in st.session_state:
        df = st.session_state[f"{P}_pool"]
        fig = go.Figure()
        for j, d in enumerate(df["diseño"].unique()):
            sub = df[df["diseño"] == d]
            fig.add_trace(go.Scatter(x=sub["σ₂/σ₁"], y=sub["cobertura"], mode="lines+markers", name=f"n₁, n₂ = {d}",
                                     line=dict(color=gr.SERIES[j % 3], width=2), marker=dict(size=9),
                                     error_y=dict(type="data", array=1.96 * sub["ee"], color=gr.SERIES[j % 3])))
        fig.add_hline(y=1 - alfa, line=dict(color=gr.TINTA, dash="dot"))
        gr._base(fig, "Cobertura de la t agrupada según σ₂/σ₁", 420, x="σ₂/σ₁", y="Cobertura")
        ui.mostrar_figura(fig, "experimento6_t_agrupada", f"{P}_pool_fig")
        st.dataframe(df.style.format({"cobertura": "{:.4f}", "ee": "{:.4f}", "aproximación (complementaria)": "{:.4f}"}),
                     hide_index=True, use_container_width=True)
        st.markdown(r"""
**Por qué.** $S_p^2$ pondera cada varianza muestral por sus grados de libertad. Si la muestra **grande** viene de la
población con varianza **pequeña**, $S_p^2$ subestima la variabilidad real de $\bar Y_1-\bar Y_2$, que es
$\sigma_1^2/n_1+\sigma_2^2/n_2$. El intervalo queda demasiado estrecho y cubre menos. En el caso contrario, cubre de más.
Con $n_1=n_2$ los pesos coinciden y $S_p^2(1/n_1+1/n_2)=(S_1^2+S_2^2)/n$ estima exactamente la varianza correcta.
La columna «aproximación» es $2\Phi(z_{\alpha/2}/R)-1$, con $R^2=\dfrac{\sigma_1^2/n_1+\sigma_2^2/n_2}{E(S_p^2)(1/n_1+1/n_2)}$
(cálculo complementario para muestras grandes).
""")

# ======================================================================
with t_res:
    st.markdown("Resumen de qué es **exacto** (vale para todo n bajo los supuestos) y qué es **asintótico** (vale cuando n → ∞). "
                "La convergencia en distribución del TCL no dice nada sobre un n concreto: por eso se simula.")
    res = pd.DataFrame([
        ["Z con σ conocida", "Teo. 7.1", "Población normal", "Exacto", "Aproximado (TCL)", "Sí"],
        ["Z con S, muestra grande", "Sec. 8.6", "n grande", "Aproximado aun con normalidad", "Aproximado", "Sí"],
        ["t para μ", "Teo. 7.1, 7.3, Def. 7.2", "Población normal", "Exacto", "Aproximado; robusto (Sec. 8.10)", "Sí"],
        ["χ² para σ²", "Teo. 7.3", "Población normal", "Exacto", "Incorrecto (Sec. 8.9)", "No: converge a otro valor"],
        ["Proporción p", "Sec. 7.5, 8.6", "n grande, p lejos de 0 y 1", "Aproximado", "Muy malo con p̂ ∈ {0, 1}", "Sí, pero lento cerca de 0 o 1"],
        ["μ₁ − μ₂, t agrupada", "Sec. 8.8", "Normalidad, σ₁ = σ₂, independencia", "Exacto", "Incorrecto si n₁ ≠ n₂ (Sec. 8.10)", "No, si n₁/n₂ ≠ 1"],
        ["σ₂²/σ₁², F", "Def. 7.3, Ej. 8.125", "Poblaciones normales", "Exacto", "Incorrecto (como χ²)", "No"],
        ["θ exponencial, 2ΣY/θ", "Ej. 8.47", "Población exponencial", "Exacto", "Incorrecto", "No"],
    ], columns=["Procedimiento", "Base", "Supuesto clave", "Si se cumple", "Si se viola", "¿Lo arregla n grande?"])
    st.dataframe(res, hide_index=True, use_container_width=True)
    ui.nota("Las entradas «No» de la última columna para la t agrupada y la exponencial son conclusiones de este laboratorio "
            "(simulación y cálculo complementario), coherentes con las advertencias del libro, pero no están enunciadas así en él.")
