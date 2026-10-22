import numpy as np
import pandas as pd
import streamlit as st

from nucleo import fdist, graficos as gr
from nucleo import motor, teoria, ui
from nucleo.poblaciones import FORMAS, Poblacion, forma

P = "int"
ui.preparar()
ui.encabezado(
    "4. El intervalo para σ₂²/σ₁²",
    "El capítulo 8 usa la F como pivote para construir un intervalo de confianza para la razón de varianzas. Aquí se "
    "construyen miles de esos intervalos y se cuenta cuántos contienen el valor verdadero: con normalidad son el 95 %; "
    "sin normalidad, no.",
    "Sección 8.5, método del pivote (p. 406–407); Ejercicio 8.125 (p. 441); Sección 8.9 (p. 435).",
)

st.sidebar.header("Escenario")
p1 = ui.selector_poblacion(f"{P}_1", "Población 1", "normal", 1.0, mostrar_mu=False)
p2 = ui.selector_poblacion(f"{P}_2", "Población 2", "normal", 2.0, mostrar_mu=False)
st.sidebar.subheader("Muestreo")
c1, c2 = st.sidebar.columns(2)
n1 = int(c1.number_input("n₁", 2, motor.N_MAX, 12, key=f"{P}_n1"))
n2 = int(c2.number_input("n₂", 2, motor.N_MAX, 12, key=f"{P}_n2"))
conf = float(st.sidebar.number_input("Confianza (%)", 50.0, 99.9, 95.0, 0.5, key=f"{P}_conf"))
alfa = 1 - conf / 100
B = int(st.sidebar.number_input("Intervalos B", 100, motor.B_MAX, 10000, 1000, key=f"{P}_B"))
esc = motor.Escenario(p1, p2, n1, n2, B, 2026)
ui.costo(esc)
bloq = ui.mostrar_errores(esc.validar())
if ui.boton(P, deshabilitado=bloq):
    b, av = ui.barra()
    r = ui.simular(esc, av)
    b.empty()
    ui.guardar(P, (esc, alfa), r)

t_uno, t_n, t_porq = st.tabs(["Los intervalos", "¿Mejora con más datos?", "Por qué es el mismo problema que la F"])

with t_uno:
    res, viejo = ui.recuperar(P, (esc, alfa))
    if res is None:
        st.info("Pulsa «Ejecutar simulación». Empieza con las dos poblaciones normales y luego cambia a exponencial o t.")
    else:
        if viejo:
            ui.aviso_desactualizado()
        E = res.escenario
        theta = E.pob2.varianza / E.pob1.varianza
        L, U = fdist.intervalo_razon(res.s2_1, res.s2_2, E.n1, E.n2, alfa)
        dentro = (L <= theta) & (theta <= U)
        cob = motor.Proporcion(int(dentro.sum()), E.B, 1 - alfa)
        ui.cadena(E.pob1.forma, E.pob2.forma, cob.estimada, 1 - alfa)
        c = st.columns(4)
        c[0].metric("σ₂²/σ₁² verdadero", f"{theta:g}")
        c[1].metric("Cobertura real", f"{100 * cob.estimada:.2f} %")
        c[2].metric("Prometida", f"{100 * (1 - alfa):.1f} %")
        c[3].metric("Error estándar Monte Carlo", f"{100 * cob.error_estandar:.2f} pts")
        if cob.compatible():
            ui.veredicto("<b>La promesa se cumple.</b> La diferencia con el nivel prometido se explica por el azar de la simulación.", True)
        else:
            ui.veredicto(f"<b>La promesa no se cumple.</b> La diferencia ({100 * (cob.estimada - (1 - alfa)):+.1f} puntos) "
                         f"está a {abs(cob.z()):.0f} errores estándar: no es azar." +
                         (" Los intervalos fallan más de lo prometido, así que la incertidumbre real es mayor que la que reportan."
                          if cob.estimada < 1 - alfa else " Los intervalos son más anchos de lo necesario."), False)
        k = st.slider("Intervalos a dibujar", 20, 150, 60, 10, key=f"{P}_k")
        ui.figura(gr.intervalos(L[:k], U[:k], theta, f"Los primeros {k} intervalos del {conf:g} % para σ₂²/σ₁²"),
                  "intervalos_razon", f"{P}_iv")
        ui.nota("El eje está en escala logarítmica porque el intervalo es para una razón: es asimétrico alrededor de s₂²/s₁², "
                "igual que la F.")
        t = pd.DataFrame({"replica": np.arange(1, E.B + 1), "S1_2": res.s2_1, "S2_2": res.s2_2, "L": L, "U": U,
                          "contiene": dentro})
        ui.tabla_descarga(t, "intervalos_razon", P)

with t_n:
    st.markdown("Para la forma de la barra lateral (la misma en las dos poblaciones), se repite el experimento con varios n "
                "y se dibuja la cobertura real. Se pueden añadir otras dos formas para comparar.")
    extra = st.multiselect("Comparar además con", [k for k in FORMAS if k != p1.forma.clave],
                           default=["normal"] if p1.forma.clave != "normal" else ["exponencial"],
                           format_func=lambda k: FORMAS[k].nombre, key=f"{P}_extra", max_selections=2)
    ns = st.multiselect("Valores de n₁ = n₂", [5, 10, 20, 50, 100, 300, 1000], default=[5, 10, 20, 50, 100, 300, 1000],
                        key=f"{P}_ns")
    Bn = int(st.number_input("B por cada n", 500, 50000, 5000, 500, key=f"{P}_Bn"))
    if st.button("Calcular la cobertura según n", type="primary", key=f"{P}_bn", disabled=not ns):
        b, av = ui.barra("Simulando…")
        formas = [p1.forma] + [forma(k) for k in extra]
        series, lims = [], []
        for i, fo in enumerate(formas):
            sub = lambda fr, i=i: av((i + fr) / len(formas))
            df = ui.cacheado(("int_n", fo, tuple(sorted(ns)), Bn, alfa),
                             lambda fo=fo, sub=sub: motor.barrido_n(fo, fo, sorted(ns), Bn, alfa, 2026, progreso=sub))
            series.append((fo.nombre_corto(), df))
            lims.append((fo.nombre_corto(), teoria.cobertura_limite(fo.curtosis(), alfa)))
        b.empty()
        st.session_state[f"{P}_n_res"] = (series, lims, Bn, alfa)
    if f"{P}_n_res" in st.session_state:
        series, lims, Bn, a_ = st.session_state[f"{P}_n_res"]
        ui.figura(gr.cobertura_vs_n(series, 1 - a_, "Cobertura real según el tamaño de las muestras", lims, Bn),
                  "intervalo_cobertura_vs_n", f"{P}_cvn")
        ui.veredicto("<b>Lectura.</b> Con la normal, la cobertura es la prometida para todo n. Con colas pesadas cae y "
                     "se estanca en el límite (línea discontinua): más datos no la devuelven al nivel prometido. Con colas "
                     "livianas queda por encima. Es la misma advertencia que hace el libro para el intervalo de σ² en la Sección 8.9.")

with t_porq:
    st.markdown(r"""
**Paso 1.** El pivote del Ejercicio 8.125 es $F^*=\dfrac{\sigma_2^2}{\sigma_1^2}\cdot\dfrac{S_1^2}{S_2^2}$, que es exactamente
$\dfrac{S_1^2/\sigma_1^2}{S_2^2/\sigma_2^2}$, el mismo estadístico de los otros experimentos.

**Paso 2.** El intervalo se obtiene despejando el parámetro del enunciado $F_{1-\alpha/2}\le F^*\le F_{\alpha/2}$ (método del
pivote, Sección 8.5). Despejar no cambia el evento, solo lo reescribe.

**Paso 3.** Por lo tanto:
""")
    st.latex(r"P\big(\text{el intervalo contiene }\sigma_2^2/\sigma_1^2\big)=P\big(F_{1-\alpha/2}\le F^*\le F_{\alpha/2}\big).")
    st.markdown(r"""
**Paso 4.** Bajo normalidad, $F^*\sim F(n_1-1,n_2-1)$ y esa probabilidad es exactamente $1-\alpha$. Sin normalidad, $F^*$ tiene
otra distribución y la probabilidad es otra. **La cobertura del intervalo es la probabilidad central de $F^*$.**

Por eso el histograma de F* del Experimento 1 y la cobertura de este experimento cuentan la misma historia: la masa que
se sale de las colas naranjas es exactamente la proporción de intervalos que fallan.
""")
