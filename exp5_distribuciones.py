import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from lab import graficos as gr
from lab import intervalos as ic
from lab import motor, teoria, ui
from lab.poblaciones import CONTINUAS_O_MEDIA, Poblacion

P = "e5"
ui.preparar()
ui.encabezado(
    "Experimento 5. Distribuciones muestrales",
    "Los intervalos del capítulo 8 se construyen con las distribuciones muestrales del capítulo 7. Aquí se ven como "
    "histogramas de miles de réplicas frente a las densidades que dan los teoremas, y se ve qué pasa cuando sus "
    "hipótesis no se cumplen.",
    "Definición 7.1, Teoremas 7.1, 7.3 y 7.4, Definición 7.2, Sección 7.5, Ejemplo 8.1 y Definición 8.4.",
)

st.sidebar.header("Población y muestreo")
pob = ui.selector_poblacion(f"{P}_pob", CONTINUAS_O_MEDIA, "Distribución de la población", "exponencial")
n = int(st.sidebar.number_input("Tamaño de cada muestra n", 2, motor.N_MAXIMO, 5, key=f"{P}_n"))
B = int(st.sidebar.number_input("Número de muestras B", 100, 200000, 20000, step=1000, key=f"{P}_B"))
semilla = int(st.sidebar.number_input("Semilla aleatoria", 0, 2**31 - 1, 2026, key=f"{P}_sem"))
err = pob.validar()
if n * B > motor.LIMITE_OBSERVACIONES:
    err.append("n × B supera el límite computacional; reduce n o B.")
st.sidebar.markdown(f'<div class="lab-costo">{ui.entero(B)} muestras de tamaño {ui.entero(n)}: '
                    f'{ui.entero(n * B)} números aleatorios.</div>', unsafe_allow_html=True)
bloqueado = ui.mostrar_errores(err)


def generar(pob: Poblacion, n: int, B: int, semilla: int, _progreso=None):
    return ui._cacheado(("exp5", pob, n, B, semilla), lambda: motor.estadisticos_una_muestra(
        pob, n, B, np.random.default_rng(semilla), _progreso))


firma = (pob, n, B, semilla)
if ui.boton_ejecutar(P, bloqueado, "Generar las muestras"):
    barra, avance = ui.barra_progreso("Generando las muestras…")
    est = generar(pob, n, B, semilla, avance)
    barra.empty()
    ui.guardar(P, firma, est)

est, viejo = ui.recuperar(P, firma)
if est is None:
    st.info("Elige la población, n y B, y pulsa «Generar las muestras». Sugerencia: compara la exponencial con la normal, "
            "con n = 5 y luego con n = 25, como las Figuras 7.6 y 7.7 del libro.")
    st.stop()
if viejo:
    ui.aviso_desactualizado()
pob, n, B, semilla = st.session_state[f"{P}_resultado"][0]
mu, var = pob.media(), pob.varianza()
sd = np.sqrt(var)
media, s2 = est["media"], est["var"]
normal = pob.espec.es_normal
finita = np.isfinite(var)

tabs = st.tabs(["Media muestral", "Varianza muestral", "t de Student", "Independencia de Ȳ y S²",
                "Del capítulo 7 al 8", "Sesgo y MSE", "Binomial y normal"])

# ------------------------------------------------------------------ media
with tabs[0]:
    curvas = []
    if finita:
        curvas.append(("N(μ, σ²/n): Teorema 7.1 (exacta) o TCL (aproximada)",
                       stats.norm(mu, sd / np.sqrt(n)).pdf, "discontinua"))
    exacta = teoria.densidad_media_exacta(pob, n)
    if exacta is not None and not normal:
        curvas.append(("Densidad exacta de Ȳ (gamma, por FGM)", exacta, "solida"))
    fig = gr.histograma_densidades(media, curvas, f"Distribución muestral de Ȳ con n = {n}", x="ȳ",
                                   discreto=False)
    ui.mostrar_figura(fig, "experimento5_media", f"{P}_media")
    tabla = pd.DataFrame({
        "": ["Media de los ȳ", "Varianza de los ȳ", "Asimetría de los ȳ"],
        "Simulación": [media.mean(), media.var(ddof=1), stats.skew(media)],
        "Teoría": [mu, var / n if finita else np.inf, np.nan],
    })
    if pob.clave in ("exponencial",):
        tabla.loc[2, "Teoría"] = 2 / np.sqrt(n)
    if pob.clave == "gamma":
        tabla.loc[2, "Teoría"] = 2 / np.sqrt(n * pob.p["alpha"])
    if normal or pob.clave in ("uniforme", "t", "dado"):
        tabla.loc[2, "Teoría"] = 0.0
    c1, c2 = st.columns([3, 2])
    with c1:
        st.dataframe(tabla.style.format({"Simulación": "{:.5f}", "Teoría": "{:.5f}"}), hide_index=True, use_container_width=True)
    with c2:
        if normal:
            ui.veredicto("<b>Población normal:</b> Ȳ es exactamente normal para todo n (Teorema 7.1).")
        elif finita:
            ui.veredicto("<b>Población no normal:</b> la normal es solo una aproximación (TCL, Teorema 7.4). "
                         "Para n pequeño se nota la asimetría heredada de la población; al aumentar n desaparece.")
        else:
            ui.veredicto("<b>Varianza infinita:</b> no se cumple la hipótesis σ² < ∞ del Teorema 7.4. Ȳ no se "
                         "concentra como 1/√n y el histograma tiene colas muy largas.")
    st.markdown(r"""
**Qué comprobar.** E$(\bar Y)=\mu$ y $V(\bar Y)=\sigma^2/n$ valen **para cualquier población** con varianza finita
(Capítulo 5; recordado en la p. 370), y la Tabla 7.1 del libro hace esta misma comparación con 1000 muestras exponenciales.
La **forma** normal es exacta solo si la población es normal; en otro caso es el TCL.
Para la exponencial, la asimetría de $\bar Y$ es $2/\sqrt n$: con $n=5$ vale $0.89$ y con $n=25$, $0.4$. Por eso la Figura 7.6
se ve «ligeramente sesgada» y la 7.7 «casi simétrica».
""")

# ------------------------------------------------------------------ varianza
with tabs[1]:
    if not finita:
        st.warning("La población tiene varianza infinita: σ² no existe y (n − 1)S²/σ² no está definido.")
    else:
        W = (n - 1) * s2 / var
        curvas = [(f"χ² con {n - 1} gl (Teorema 7.3)", stats.chi2(n - 1).pdf, "solida")]
        rango = (0, float(np.quantile(W, 0.995)))
        fig = gr.histograma_densidades(W, curvas, "Distribución de (n − 1)S²/σ²", x="(n − 1)s²/σ²", rango=rango)
        ui.mostrar_figura(fig, "experimento5_chi2", f"{P}_chi2")
        tab = pd.DataFrame({
            "": ["Media de W", "Varianza de W", "P(W > χ²_.05)", "P(W < χ²_.95)"],
            "Simulación": [W.mean(), W.var(ddof=1), np.mean(W > ic.chi2_critico(.05, n - 1)), np.mean(W < ic.chi2_critico(.95, n - 1))],
            "χ²(n − 1)": [n - 1, 2 * (n - 1), 0.05, 0.05],
        })
        st.dataframe(tab.style.format({"Simulación": "{:.4f}", "χ²(n − 1)": "{:.4f}"}), hide_index=True, use_container_width=True)
        k = pob.curtosis_exceso()
        if normal:
            ui.veredicto("<b>Población normal:</b> el histograma coincide con la χ²(n − 1) del Teorema 7.3.")
        else:
            ui.veredicto(
                f"<b>Población no normal:</b> la media de W sigue siendo n − 1, porque E(S²) = σ² para cualquier población "
                f"(Ejemplo 8.1). Pero la varianza de W ya no es 2(n − 1): para n grande es aproximadamente (n − 1)(2 + κ), "
                f"con κ la curtosis en exceso (κ = {k:.2f} aquí; resultado complementario, no del libro). "
                "El intervalo χ² usa los cuantiles equivocados, y esa es la causa de su fragilidad (Sección 8.9).")

# ------------------------------------------------------------------ t
with tabs[2]:
    with np.errstate(divide="ignore", invalid="ignore"):
        T = np.sqrt(n) * (media - mu) / np.sqrt(s2)
    lim = max(4.0, float(min(8, np.quantile(np.abs(T), 0.995))))
    curvas = [(f"t con {n - 1} gl (Definición 7.2)", stats.t(n - 1).pdf, "solida"),
              ("N(0, 1)", stats.norm.pdf, "discontinua")]
    fig = gr.histograma_densidades(T, curvas, "Distribución de T = √n(Ȳ − μ)/S", x="t", rango=(-lim, lim), bins=80)
    ui.mostrar_figura(fig, "experimento5_t", f"{P}_t")
    z = ic.z_critico(0.025)
    t = ic.t_critico(0.025, n - 1)
    tab = pd.DataFrame({
        "Probabilidad": [f"P(|T| > {z:.3f})  [z.025]", f"P(|T| > {t:.3f})  [t.025, {n - 1} gl]"],
        "Simulación": [np.mean(np.abs(T) > z), np.mean(np.abs(T) > t)],
        "Si T ~ t(n − 1)": [2 * stats.t.sf(z, n - 1), 0.05],
        "Si T ~ N(0, 1)": [0.05, 2 * stats.norm.sf(t)],
    })
    st.dataframe(tab.style.format({c: "{:.4f}" for c in tab.columns[1:]}), hide_index=True, use_container_width=True)
    st.markdown(r"""
**Lectura.** La primera fila es la probabilidad de que el intervalo $\bar Y\pm z_{.025}S/\sqrt n$ **no** contenga a $\mu$.
Si la población es normal y $n$ es pequeño, esa probabilidad es bastante mayor que .05, porque $T$ tiene colas más pesadas
que $Z$ ($V(T)=\nu/(\nu-2)$). Con $t_{.025}$ se recupera exactamente .05: esa es la razón de ser de la Sección 8.8.
Con una población asimétrica, $T$ además se vuelve asimétrica para $n$ pequeño. El histograma lo muestra.
""")

# ------------------------------------------------------------------ independencia
with tabs[3]:
    m = min(B, 4000)
    if finita:
        r = float(np.corrcoef(media, s2)[0, 1])
    else:
        r = float(stats.spearmanr(media[:m], s2[:m])[0])
    fig = gr.dispersion(media, s2, f"Cada punto es una muestra (se muestran {ui.entero(m)})", "ȳ", "s²", m)
    ui.mostrar_figura(fig, "experimento5_independencia", f"{P}_ind")
    ui.veredicto(f"Correlación entre Ȳ y S² en las {ui.entero(B)} réplicas: <b>{r:.3f}</b>. " +
                 ("Bajo normalidad, el Teorema 7.3 garantiza independencia: la nube no muestra ninguna tendencia."
                  if normal else
                  "Fuera de la normalidad, Ȳ y S² dejan de ser independientes. Con poblaciones asimétricas a la derecha, "
                  "las muestras con media alta suelen tener también varianza alta."))
    st.markdown(r"""
**Por qué importa para los intervalos.** La Definición 7.2 exige que $Z$ y $W$ sean **independientes** para que
$T=Z/\sqrt{W/\nu}$ tenga distribución $t$. Esa independencia sale del Teorema 7.3 y solo vale bajo normalidad.
Si $\bar Y$ y $S$ están correlacionados positivamente, cuando $\bar Y$ cae lejos por encima de $\mu$ el intervalo también
se ensancha, y cuando cae por debajo se estrecha. El resultado es un intervalo t con cobertura desigual en las dos colas.
""")

# ------------------------------------------------------------------ cap 7 → cap 8
with tabs[4]:
    st.markdown(r"""
**La conexión.** Un intervalo de confianza no es más que un enunciado de probabilidad sobre el pivote, reescrito.
Para el intervalo t:
$$\bar Y-t_{\alpha/2}\tfrac{S}{\sqrt n}\le\mu\le\bar Y+t_{\alpha/2}\tfrac{S}{\sqrt n}\iff -t_{\alpha/2}\le T\le t_{\alpha/2}.$$
Son **el mismo evento** escrito de dos formas. Así que la fracción de réplicas con $T$ en la zona sombreada es
**exactamente** la fracción de intervalos que contienen a $\mu$. La cobertura del capítulo 8 es un área bajo la
distribución muestral del capítulo 7.
""")
    conf = st.select_slider("Nivel de confianza", [80, 90, 95, 98, 99], 95, key=f"{P}_conf")
    a = 1 - conf / 100
    tc = ic.t_critico(a / 2, n - 1)
    dentro = np.abs(T) <= tc
    L, U = ic.media_t(media, np.sqrt(s2), n, a)
    cubre = ic.contiene(L, U, mu)
    fig = gr.histograma_densidades(T, [(f"t con {n - 1} gl", stats.t(n - 1).pdf, "solida")],
                                   "Pivote T y la región −t ≤ T ≤ t", x="t", rango=(-lim, lim), sombrear=(-tc, tc), bins=80)
    ui.mostrar_figura(fig, "experimento5_pivote", f"{P}_piv")
    c = st.columns(3)
    c[0].metric("Réplicas con |T| ≤ t_{α/2}", f"{dentro.mean():.4f}")
    c[1].metric("Intervalos t que contienen μ", f"{cubre.mean():.4f}")
    c[2].metric("¿Coinciden réplica a réplica?", "Sí" if np.array_equal(dentro, cubre) else "No")
    ui.nota("Las dos proporciones coinciden porque, réplica por réplica, «|T| ≤ t» y «μ ∈ IC» son la misma afirmación.")

# ------------------------------------------------------------------ sesgo
with tabs[5]:
    if not finita:
        st.warning("Con varianza infinita, σ² no existe.")
    else:
        s2p = s2 * (n - 1) / n
        filas = []
        for nombre, v in (("S² (divisor n − 1)", s2), ("S′² (divisor n)", s2p)):
            sesgo = v.mean() - var
            filas.append({"Estimador": nombre, "Media simulada": v.mean(), "Sesgo simulado": sesgo,
                          "Sesgo teórico": 0.0 if "n − 1" in nombre else -var / n,
                          "Varianza simulada": v.var(ddof=1), "MSE simulado": np.mean((v - var) ** 2)})
        dfb = pd.DataFrame(filas)
        if normal:
            dfb["MSE teórico (normal)"] = [2 * var**2 / (n - 1), (2 * n - 1) * var**2 / n**2]
        st.dataframe(dfb.style.format({c: "{:.5f}" for c in dfb.columns if c != "Estimador"}), hide_index=True,
                     use_container_width=True)
        rango = (0, float(np.quantile(s2, 0.995)))
        fig = go.Figure()
        for i, (nombre, v) in enumerate((("S²", s2), ("S′²", s2p))):
            fig.add_trace(go.Histogram(x=v, histnorm="probability density", name=nombre, opacity=0.6, nbinsx=80,
                                       marker=dict(color=gr.SERIES[i], line=dict(color="white", width=0.5))))
            fig.add_vline(x=v.mean(), line=dict(color=gr.SERIES[i], width=2))
        fig.add_vline(x=var, line=dict(color=gr.TINTA, width=2, dash="dash"), annotation_text=f"σ² = {var:.4g}",
                      annotation_position="top right")
        gr._base(fig, "S² frente a S′²: las líneas verticales de color son las medias simuladas", 380,
                 x="Estimación de σ²", y="Densidad")
        fig.update_layout(barmode="overlay")
        fig.update_xaxes(range=list(rango))
        ui.mostrar_figura(fig, "experimento5_sesgo", f"{P}_sesgo")
        st.markdown(r"""
**Ejemplo 8.1 (p. 398).** $E(S^2)=\sigma^2$ y $E(S'^2)=\frac{n-1}{n}\sigma^2$, así que el sesgo de $S'^2$ es $-\sigma^2/n$.
Esto vale **para cualquier población** con varianza finita. Compruébalo cambiando la población.

**Definición 8.4.** $\mathrm{MSE}=V+B^2$. Ser insesgado no implica tener menor MSE. Bajo normalidad,
$\mathrm{MSE}(S^2)=\frac{2\sigma^4}{n-1}$ y $\mathrm{MSE}(S'^2)=\frac{(2n-1)\sigma^4}{n^2}$, que es **menor** (complementario).
El intervalo χ² usa $S^2$ porque el pivote del Teorema 7.3 está escrito con $(n-1)S^2=\sum(Y_i-\bar Y)^2$.
""")

# ------------------------------------------------------------------ binomial
with tabs[6]:
    st.markdown("Independiente de la población elegida: aquí $Y\\sim$ Binomial$(n_b, p)$ (Sección 7.5).")
    c1, c2 = st.columns(2)
    nb = int(c1.number_input("n (ensayos)", 1, 5000, 25, key=f"{P}_nb"))
    pb = float(c2.number_input("p", 0.001, 0.999, 0.4, step=0.01, key=f"{P}_pb"))
    y = np.arange(nb + 1)
    pmf = stats.binom.pmf(y, nb, pb)
    m_, s_ = nb * pb, np.sqrt(nb * pb * (1 - pb))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=y, y=pmf, name="Binomial exacta", marker=dict(color="rgba(42,120,214,0.55)",
                                                                         line=dict(color="white", width=1))))
    xs = np.linspace(max(-0.5, m_ - 5 * s_), min(nb + 0.5, m_ + 5 * s_), 500)
    fig.add_trace(go.Scatter(x=xs, y=stats.norm.pdf(xs, m_, s_), name="N(np, np(1 − p))",
                             line=dict(color=gr.TINTA, width=2.2)))
    gr._base(fig, "Aproximación normal a la binomial", 380, x="y", y="Probabilidad / densidad")
    fig.update_xaxes(range=[max(-0.5, m_ - 5 * s_), min(nb + 0.5, m_ + 5 * s_)])
    ui.mostrar_figura(fig, "experimento5_binomial", f"{P}_bin")
    regla = teoria.regla_binomial(nb, pb)
    ui.veredicto(f"Regla p ± 3√(pq/n) ∈ (0, 1): <b>{'se cumple' if regla else 'NO se cumple'}</b> "
                 f"(p − 3√(pq/n) = {pb - 3 * np.sqrt(pb * (1 - pb) / nb):.3f}, p + 3√(pq/n) = {pb + 3 * np.sqrt(pb * (1 - pb) / nb):.3f}).")
    yy = int(st.number_input("Comparar P(Y ≤ y) para y =", 0, nb, min(8, nb), key=f"{P}_yy"))
    tab = pd.DataFrame({
        "Cantidad": [f"P(Y ≤ {yy})", f"P(Y = {yy})"],
        "Exacta (binomial)": [stats.binom.cdf(yy, nb, pb), stats.binom.pmf(yy, nb, pb)],
        "Normal sin corrección": [stats.norm.cdf(yy, m_, s_), np.nan],
        "Normal con corrección ±0.5": [stats.norm.cdf(yy + 0.5, m_, s_),
                                       stats.norm.cdf(yy + 0.5, m_, s_) - stats.norm.cdf(yy - 0.5, m_, s_)],
    })
    st.dataframe(tab.style.format({c: "{:.4f}" for c in tab.columns[1:]}, na_rep="—"), hide_index=True, use_container_width=True)
    ui.nota("Con n = 25, p = .4 e y = 8 se reproduce el Ejemplo 7.11 (p. 381): exacta .274 y .120; aproximadas .2709 y .1170. "
            "El libro usa tablas, así que su .2709 sale de redondear z a −.61.")
