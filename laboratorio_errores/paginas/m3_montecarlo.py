import streamlit as st

from nucleo import binomial as bn
from nucleo import estado
from nucleo import graficos as gr
from nucleo import montecarlo as mc
from nucleo import pruebaz as pz
from nucleo import ui
from nucleo.ui import ALFA, BETA, NAVY

ui.preparar()
ss = st.session_state
PRUEBAS = ("Prueba Z (Módulo 2)", "Binomial de Jones (Módulo 1)")
ESCENARIOS = {"Solo H0 verdadera (estimar α)": 1.0, "Solo Ha verdadera (estimar β)": 0.0, "Mitad H0, mitad Ha": 0.5}

ui.encabezado(
    "Módulo 3 · Experimento Monte Carlo",
    "Las fórmulas dicen con qué probabilidad se equivoca la regla. Aquí se repite el experimento completo miles "
    "de veces y se cuentan las equivocaciones de verdad.",
    "Extensión computacional de la Sección 10.2: α y β son probabilidades de eventos, así que la frecuencia "
    "relativa de esos eventos en experimentos independientes se acerca a ellas.")

col_c, col_r = st.columns([1, 2.3], gap="large")
with col_c:
    st.subheader("Diseño del experimento")
    st.radio("Prueba", PRUEBAS, key="mc_prueba")
    st.radio("Estado verdadero en cada experimento", list(ESCENARIOS), key="mc_escenario")
    st.select_slider("Número de experimentos m", [100, 500, 1000, 5000, 10000, 20000, 50000], key="mc_m")
    st.number_input("Semilla", min_value=0, max_value=10**9, step=1, key="mc_semilla",
                    help="Con la misma semilla se repiten exactamente los mismos experimentos.")
    es_z = ss.mc_prueba == PRUEBAS[0]
    ok, msg = estado.z_valida() if es_z else estado.binom_valida()
    if es_z and ok:
        cfg = estado.config_z()
        r = pz.resumen(cfg)
        a_teo, b_teo = r["alfa"], r["beta"]
        st.caption(f"μ₀ = {cfg.mu0:g}, μ₁ = {cfg.mu1:g}, σ = {cfg.sigma:g}, n = {cfg.n}, α = {cfg.alfa:g}, "
                   f"{'Hₐ: μ > μ₀' if cfg.cola == 'superior' else 'Hₐ: μ < μ₀'}. Se cambian en el Módulo 2.")
    elif ok:
        b = estado.binom()
        a_teo = bn.alfa(b["n"], b["p0"], b["c"], b["cola"])
        b_teo = bn.beta(b["n"], b["p1"], b["c"], b["cola"])
        st.caption(f"n = {b['n']}, p₀ = {b['p0']:.2f}, p₁ = {b['p1']:.2f}, "
                   f"RR = {{y {'≤' if b['cola'] == 'inferior' else '≥'} {b['c']}}}. Se cambian en el Módulo 1.")
    else:
        st.error(msg)
    simular = st.button("Simular", type="primary", width="stretch", disabled=not ok)

if simular:
    m, sem, ph0 = int(ss.mc_m), int(ss.mc_semilla), ESCENARIOS[ss.mc_escenario]
    with st.spinner("Simulando experimentos…"):
        if es_z:
            df = mc.simular_z(cfg, m, ph0, sem)
            params = pz.como_dict(cfg)
        else:
            df = mc.simular_binomial(b["n"], b["p0"], b["p1"], b["c"], b["cola"], m, ph0, sem)
            params = dict(b)
    ss.mc_res = {"df": df, "prueba": ss.mc_prueba, "alfa": a_teo, "beta": b_teo, "params": params,
                 "escenario": ss.mc_escenario}

res = ss.get("mc_res")
with col_r:
    if res is None:
        st.info("Elige el diseño y pulsa **Simular**. Cada experimento genera una muestra completa, calcula el "
                "estadístico, aplica la regla y anota si hubo error tipo I, error tipo II o decisión correcta.")
        st.stop()
    df = res["df"]
    st.caption(f"Último resultado: {res['prueba']}, escenario «{res['escenario']}», m = {len(df):,} experimentos."
               .replace(",", "."))
    tabla = mc.resumen(df, res["alfa"], res["beta"])
    items = []
    for _, f in tabla.iterrows():
        color = ALFA if "I (" in f["Probabilidad"] else BETA
        items.append((f"{f['Probabilidad']}: frecuencia empírica", ui.fmt(f["Frecuencia empírica"]),
                      f"teórica {f['Teórica']:.4f} · error MC ± {f['Error Monte Carlo']:.4f}", color))
    correctas = float((df["resultado"] == mc.OK).mean())
    items.append(("Decisiones correctas", ui.fmt(correctas, 3), f"de {len(df):,} experimentos".replace(",", "."), NAVY))
    ui.cifras(items)
    t1 = mc.trayectoria(df, mc.H0_V, mc.ERR1)
    t2 = mc.trayectoria(df, mc.HA_V, mc.ERR2)
    st.plotly_chart(gr.trayectorias(t1, res["alfa"], t2, res["beta"]), width="stretch")

st.header("Teórico contra empírico")
st.dataframe(tabla.style.format({"Teórica": "{:.5f}", "Frecuencia empírica": "{:.5f}", "Error Monte Carlo": "{:.5f}",
                                 "Diferencia / EE teórico": "{:+.2f}", "Experimentos con ese estado": "{:,}"}),
             hide_index=True, width="stretch")
st.markdown(
    "**Error Monte Carlo** = $\\sqrt{\\hat p(1-\\hat p)/m}$: el error estándar de una proporción estimada con m "
    "experimentos. La última columna mide la distancia entre lo simulado y lo teórico en errores estándar; "
    "valores entre −2 y 2 son lo esperable por puro azar. La banda sombreada de la gráfica es "
    "teórica ± 1.96·EE: se angosta como $1/\\sqrt m$.")

c1, c2 = st.columns([1, 1.3], gap="large")
with c1:
    st.plotly_chart(gr.conteo_resultados(df), width="stretch")
with c2:
    st.subheader("Los primeros experimentos")
    st.dataframe(df.head(15), hide_index=True, width="stretch",
                 column_config={"media_muestral": st.column_config.NumberColumn("ȳ", format="%.4f"),
                                "z": st.column_config.NumberColumn("z", format="%.3f")})
    ui.enlace("paginas/excel.py", "Llevar estos experimentos a Excel y recontarlos allá")
