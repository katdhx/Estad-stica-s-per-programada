import numpy as np
import pandas as pd
import streamlit as st

from lab import graficos as gr
from lab import intervalos as ic
from lab import motor, teoria, ui
from lab.poblaciones import crear
from lab.procedimientos import DOS_MUESTRAS, DOS_PROPORCIONES, PROPORCION, UNA_MUESTRA

P = "e2"
ui.preparar()
ui.encabezado(
    "Experimento 2. Tamaño muestral",
    "¿Qué le pasa a un intervalo cuando la muestra crece de 5 a 100 000 observaciones? Su amplitud cae como 1/√n, "
    "su centro se concentra alrededor del parámetro y, si el procedimiento es bueno, la cobertura se mantiene.",
    "Teorema 7.1 y Tabla 8.1 (σ/√n), Sección 8.6, Sección 8.7 (tamaño muestral) y Ejemplos 8.9–8.10.",
)

REJILLA = [5, 10, 20, 30, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]

esc, errores = ui.selector_escenario(P, mostrar_n=False, B_defecto=400, B_max=20000, permitir_lado=False,
                                     proc_defecto="media_t", pob_defecto="exponencial")
st.sidebar.subheader("Tamaños muestrales")
ns = st.sidebar.multiselect("Valores de n a comparar", REJILLA, default=[5, 10, 30, 100, 1000, 10000, 100000],
                            key=f"{P}_ns")
ns = sorted(ns)
dos = esc.proc.familia in (DOS_MUESTRAS, DOS_PROPORCIONES)
if dos:
    ui.nota("En los procedimientos de dos muestras se usa n₁ = n₂ = n.")
minimo = 2 if esc.proc.clave not in ("media_z_sigma", "exponencial_chi2", "proporcion_wald", "dif_proporciones") else 1
ns = [n for n in ns if n >= minimo]
if not ns:
    errores = errores + ["Elige al menos un tamaño muestral."]
por_n = 1 if esc.proc.familia in (PROPORCION, DOS_PROPORCIONES) else None
total = sum((2 if dos else 1) * (1 if por_n else n) * esc.B for n in ns)
if total > motor.LIMITE_OBSERVACIONES:
    errores = errores + [f"El barrido pediría {ui.entero(total)} observaciones; el límite es "
                         f"{ui.entero(motor.LIMITE_OBSERVACIONES)}. Reduce B o quita los n más grandes."]
st.sidebar.markdown(f'<div class="lab-costo">Para cada n se generan B = {ui.entero(esc.B)} muestras independientes. '
                    f'En total, {ui.entero(total)} números aleatorios.</div>', unsafe_allow_html=True)
bloqueado = ui.mostrar_errores([e for e in errores if "tamaño muestral n debe" not in e])
firma = (esc, tuple(ns))
if ui.boton_ejecutar(P, bloqueado):
    barra, avance = ui.barra_progreso("Simulando cada tamaño muestral…")
    df = ui.barrido_cache(esc, tuple(ns), None, None, avance)
    barra.empty()
    ui.guardar(P, firma, df)

tab_muchas, tab_una, tab_n, tab_fund = st.tabs(
    ["Muchas muestras para cada n", "Una sola muestra que crece", "¿Qué n necesito? (Sección 8.7)", "Fundamentación matemática"]
)

with tab_muchas:
    df, viejo = ui.recuperar(P, firma)
    if df is None:
        st.info("Elige el procedimiento, la población y los tamaños muestrales, y pulsa «Ejecutar simulación».")
    else:
        if viejo:
            ui.aviso_desactualizado()
        E = st.session_state[f"{P}_resultado"][0][0]
        proc = E.proc
        etiquetas = {proc.clave: proc.nombre_corto}
        ns_ = df["n"].to_numpy()
        teo = [teoria.amplitud_esperada(proc.clave, E.pob1, int(n), E.alfa, E.pob2, int(n) if dos else None) for n in ns_]
        tv = np.array([t.valor if t.valor is not None else np.nan for t in teo], dtype=float)
        tabla = df[["n", "amplitud_media", "amplitud_de", "cobertura", "ee_cobertura", "estimador_media", "estimador_de"]].copy()
        tabla.insert(2, "amplitud_teorica", tv)
        tabla.insert(3, "empírica/teórica", tabla["amplitud_media"] / tv)
        tabla["amplitud×√n"] = tabla["amplitud_media"] * np.sqrt(tabla["n"])

        validos = np.isfinite(tabla["amplitud_media"]) & (tabla["amplitud_media"] > 0)
        if validos.sum() >= 3:
            pend = np.polyfit(np.log(tabla["n"][validos]), np.log(tabla["amplitud_media"][validos]), 1)[0]
        else:
            pend = np.nan
        c = st.columns(3)
        c[0].metric("Pendiente de log(amplitud) contra log(n)", f"{pend:.3f}", help="La teoría predice −0.5.")
        c[1].metric(f"Amplitud media con n = {ui.entero(ns_[0])}", ui.fmt(float(tabla['amplitud_media'].iloc[0])))
        c[2].metric(f"Amplitud media con n = {ui.entero(ns_[-1])}", ui.fmt(float(tabla['amplitud_media'].iloc[-1])))
        if np.isfinite(pend):
            ui.veredicto(f"En escala log-log la amplitud cae con pendiente <b>{pend:.3f}</b>. La teoría da exactamente "
                         "−1/2, porque todas las amplitudes son de la forma (constante) × (error estándar) y el error "
                         "estándar es proporcional a 1/√n. Multiplicar n por 100 divide la amplitud por 10.")

        fig = gr.curva_vs_n(df, "amplitud_media", etiquetas, "Amplitud media de los intervalos",
                            y="Amplitud (escala logarítmica)",
                            teorico={proc.clave: (ns_, tv)} if np.isfinite(tv).any() else None, logy=True)
        ui.mostrar_figura(fig, "experimento2_amplitud", f"{P}_amp")
        notas = {t.nota for t in teo if t.nota}
        for n_ in notas:
            ui.nota(f"Curva teórica: {n_}")

        cA, cB = st.columns(2)
        with cA:
            ee_teo = [teoria.error_estandar_estimador(proc.clave, E.pob1, int(n)) for n in ns_]
            dd = df.copy()
            fig2 = gr.curva_vs_n(dd, "estimador_de", etiquetas, "Variabilidad del estimador",
                                 y="Desviación estándar entre réplicas (log)",
                                 teorico={proc.clave: (ns_, np.array([np.nan if v is None else v for v in ee_teo], float))}
                                 if any(v is not None for v in ee_teo) else None, logy=True)
            ui.mostrar_figura(fig2, "experimento2_error_estandar", f"{P}_ee")
            ui.nota("Curva teórica: el error estándar de la Tabla 8.1 (σ/√n para la media, √(pq/n) para p) o "
                    "√(2σ⁴/(n−1)) para S² bajo normalidad (porque V(χ²_ν) = 2ν).")
        with cB:
            fig3 = gr.curva_vs_n(df, "cobertura", etiquetas, "Cobertura empírica", y="Proporción que contiene el parámetro",
                                 nominal=1 - E.alfa, columna_error="ee_cobertura", B=E.B)
            ui.mostrar_figura(fig3, "experimento2_cobertura", f"{P}_cob")
            ui.nota("Las barras son ±1.96 errores estándar de Monte Carlo. Que el intervalo se haga más estrecho NO "
                    "baja su cobertura: la amplitud se ajusta justo a la variabilidad del estimador.")
        st.subheader("Tabla de resultados")
        st.dataframe(tabla.style.format({c: "{:.5f}" for c in tabla.columns if c != "n"}), use_container_width=True, hide_index=True)
        ui.descargar_tabla(tabla, "experimento2_tamano_muestral", P, ui.metadatos(E))

with tab_una:
    st.markdown(
        "Aquí se genera **una sola muestra** de hasta 100 000 observaciones y se recalcula el intervalo usando sus primeras "
        "n observaciones. Es lo que hace un investigador que recoge datos uno a uno. El intervalo se estrecha alrededor del "
        "parámetro, pero esta curva **no dice nada sobre la cobertura**: es una sola realización. Para la cobertura hacen falta "
        "muchas muestras, como en la pestaña anterior."
    )
    if esc.proc.familia not in (UNA_MUESTRA, PROPORCION):
        st.info("Esta vista está disponible para los procedimientos de una muestra.")
    elif errores and any("Población" in e or "población" in e for e in errores):
        st.warning("Corrige los parámetros de la población en la barra lateral.")
    else:
        c1, c2 = st.columns([1, 3])
        nmax = c1.select_slider("Tamaño final de la muestra", [1000, 5000, 10000, 50000, 100000], 100000, key=f"{P}_nmax")
        semilla_t = int(c1.number_input("Semilla de la trayectoria", 0, 2**31 - 1, esc.semilla, key=f"{P}_semt"))
        try:
            tr = motor.trayectoria_una_muestra(esc.procedimiento, esc.pob1, int(nmax), esc.alfa, semilla_t)
            theta = float(esc.proc.verdadero(esc.pob1, None))
            with c2:
                ui.mostrar_figura(gr.trayectoria(tr, theta, ui.SIMBOLO[esc.proc.clave],
                                                 f"Una muestra que crece hasta n = {ui.entero(nmax)}"), "experimento2_trayectoria", f"{P}_tray")
            fin = tr.iloc[-1]
            ui.veredicto(f"Con las {ui.entero(fin['n'])} observaciones: intervalo [{ui.fmt(fin['L'])}, {ui.fmt(fin['U'])}], "
                         f"amplitud {ui.fmt(fin['amplitud'])}. ¿Contiene el valor verdadero {ui.fmt(theta)}? "
                         f"<b>{'Sí' if fin['cubre'] else 'No'}</b>.")
            ui.descargar_tabla(tr, "experimento2_trayectoria", f"{P}_tray")
        except motor.ErrorSimulacion as e:
            st.error(str(e))

with tab_n:
    st.markdown(
        r"La Sección 8.7 invierte la pregunta: dado un límite $B$ para el error de estimación y un nivel $1-\alpha$, "
        r"se iguala $z_{\alpha/2}\,\sigma_{\hat\theta}=B$ y se despeja $n$."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Para una media μ**")
        sig = st.number_input("σ (o una estimación de σ)", 0.0001, 1e6, 21.0, key=f"{P}_sig")
        Bm = st.number_input("Límite del error B", 0.0001, 1e6, 5.0, key=f"{P}_Bm")
        cm = st.number_input("Confianza (%)", 50.0, 99.9, 95.0, key=f"{P}_cm")
        nm = ic.n_para_media(sig, Bm, 1 - cm / 100)
        st.latex(rf"n=\left(\frac{{z_{{\alpha/2}}\,\sigma}}{{B}}\right)^2=\left(\frac{{{ic.z_critico((1 - cm / 100) / 2):.4f}\times{sig:g}}}{{{Bm:g}}}\right)^2\ \Rightarrow\ n={nm}")
        ui.nota("Con σ = 21 y B = 5 el libro usa 2σ en lugar de 1.96σ y obtiene n = 71 (p. 422); con z.025 = 1.96 sale 68.")
    with c2:
        st.markdown("**Para una proporción p**")
        p0 = st.number_input("Valor anticipado de p (0.5 si no se sabe nada)", 0.001, 0.999, 0.6, key=f"{P}_p0")
        Bp = st.number_input("Límite del error B ", 0.0001, 0.5, 0.04, format="%.4f", key=f"{P}_Bp")
        cp = st.number_input("Confianza (%) ", 50.0, 99.9, 90.0, key=f"{P}_cp")
        npp = ic.n_para_proporcion(p0, Bp, 1 - cp / 100)
        st.latex(rf"n=\frac{{z_{{\alpha/2}}^2\,p(1-p)}}{{B^2}}\ \Rightarrow\ n={npp}")
        ui.nota("Ejemplo 8.9 (p. 422): con p ≈ .6, B = .04 y 90 %, n = 406; con p = .5, n = 423.")
    st.markdown("**Comprobación por simulación.** Si se usa el n calculado, la mitad de la amplitud del intervalo "
                "Z debería quedar cerca de B con probabilidad 1 − α en el error de estimación:")
    if st.button("Comprobar la media con 2000 muestras normales", key=f"{P}_comp"):
        esc_c = motor.Escenario("media_z_sigma", crear("normal", mu=0, sigma=sig),
                                n1=int(min(nm, motor.N_MAXIMO)), B=2000, alfa=1 - cm / 100, semilla=esc.semilla)
        r = ui.simular_cache(esc_c)
        err = np.abs(r.tabla["estimador"].to_numpy())
        st.write(f"Con n = {esc_c.n1}: P(|Ȳ − μ| < B) estimada = {np.mean(err < Bm):.4f} (objetivo ≥ {cm / 100:.3f}).")

with tab_fund:
    st.markdown(r"""
**Por qué la amplitud cae como $1/\sqrt n$.** Todos los intervalos del capítulo 8 tienen la forma
$$\hat\theta\ \pm\ (\text{valor crítico})\times(\text{error estándar}),$$
y por la Tabla 8.1 (y el Teorema 7.1) el error estándar de $\bar Y$ es $\sigma/\sqrt n$. Así:

| Procedimiento | Amplitud | Comportamiento |
|---|---|---|
| Z, σ conocida | $2z_{\alpha/2}\sigma/\sqrt n$ | exactamente $\propto n^{-1/2}$ |
| t de Student | $2t_{\alpha/2,n-1}S/\sqrt n$ | $t_{\alpha/2,n-1}\downarrow z_{\alpha/2}$ y $S\to\sigma$; para $n$ grande, $\propto n^{-1/2}$ |
| Proporción | $2z_{\alpha/2}\sqrt{\hat p\hat q/n}$ | $\propto n^{-1/2}$ |
| χ² para σ² | $(n-1)S^2\big(1/\chi^2_{1-\alpha/2}-1/\chi^2_{\alpha/2}\big)$ | $\approx 2z_{\alpha/2}\sigma^2\sqrt{2/(n-1)}$ para $n$ grande |

En escala log-log, $\log A = \text{cte} - \tfrac12\log n$: una recta de pendiente $-1/2$.

**Rendimientos decrecientes.** Para reducir la amplitud a la mitad hay que **cuadruplicar** $n$. Pasar de 10 000 a 100 000
observaciones solo divide la amplitud por $\sqrt{10}\approx3.16$.

**t frente a Z.** Con $n$ pequeño, $t_{\alpha/2,n-1}$ es bastante mayor que $z_{\alpha/2}$ (con $n=5$: $2.776$ contra $1.960$ al 95 %).
Por eso la amplitud del intervalo t con $n$ pequeño queda por encima de la recta. Para $n-1>30$ son casi iguales (p. 430).

**Qué NO cambia con n.** La cobertura de un procedimiento exacto es $1-\alpha$ para **todo** $n$. En uno asintótico,
la cobertura se acerca a $1-\alpha$ al crecer $n$ (TCL). La amplitud se encoge, pero la probabilidad de contener a $\theta$ no.

**Una muestra de $10^5$ frente a $10^5$ muestras.** La primera da **un** intervalo de amplitud $\approx 2z\sigma/\sqrt{10^5}$,
que contiene o no a $\theta$. La segunda da $10^5$ intervalos con los que se estima la cobertura con error estándar
$\sqrt{(1-\alpha)\alpha/10^5}$. Son preguntas distintas: precisión de una estimación frente a fiabilidad de un procedimiento.
""")
    ui.ficha(esc.proc)
