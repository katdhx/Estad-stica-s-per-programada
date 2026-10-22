import numpy as np
import pandas as pd
import streamlit as st

from nucleo import fdist, graficos as gr
from nucleo import motor, teoria, ui

P = "con"
ui.preparar()
ui.encabezado(
    "1. Construye tu F",
    "Elige la forma, la media y la desviación estándar de cada población, y los tamaños de muestra. La app genera miles de "
    "pares de muestras, calcula F* = (S₁²/σ₁²)/(S₂²/σ₂²) en cada par y lo compara con la F(n₁−1, n₂−1) del libro.",
    "Teorema 7.3 (p. 357), Definición 7.3 (p. 362), Ejercicio 7.34 (p. 368).",
)

st.sidebar.header("Escenario")
p1 = ui.selector_poblacion(f"{P}_1", "Población 1", "exponencial", 1.0)
p2 = ui.selector_poblacion(f"{P}_2", "Población 2", "exponencial", 1.0)
st.sidebar.subheader("Muestreo")
c1, c2 = st.sidebar.columns(2)
n1 = int(c1.number_input("n₁", 2, motor.N_MAX, 10, key=f"{P}_n1"))
n2 = int(c2.number_input("n₂", 2, motor.N_MAX, 10, key=f"{P}_n2"))
B = int(st.sidebar.number_input("Pares de muestras B", 100, motor.B_MAX, 20000, 1000, key=f"{P}_B"))
semilla = int(st.sidebar.number_input("Semilla", 0, 2**31 - 1, 2026, key=f"{P}_sem"))
esc = motor.Escenario(p1, p2, n1, n2, B, semilla)
ui.costo(esc)
errores = esc.validar()
bloq = ui.mostrar_errores(errores)
if ui.boton(P, deshabilitado=bloq):
    b, av = ui.barra()
    r = ui.simular(esc, av)
    b.empty()
    ui.guardar(P, esc, r)

res, viejo = ui.recuperar(P, esc)
if res is None:
    st.info("Elige las poblaciones y pulsa «Ejecutar simulación». Sugerencia: empieza con las dos normales y después "
            "cambia una o las dos a exponencial.")
    st.stop()
if viejo:
    ui.aviso_desactualizado()
E = res.escenario
g1, g2 = E.gl
exacta = E.f_exacta
F = res.F_pivote

ui.cadena(E.pob1.forma, E.pob2.forma, motor.cobertura(res, 0.05).estimada)

tab_r, tab_a, tab_d = st.tabs(["Resultado", "Anatomía de un par de muestras", "Datos"])

with tab_r:
    col_g, col_p = st.columns([3, 2])
    with col_g:
        a, b = fdist.intervalo_central(0.05, E.n1, E.n2)
        fig = gr.histograma_f(F, g1, g2, f"F* frente a F({g1}, {g2})", region=(a, b), exacta=exacta, x="F*",
                              etiqueta_region="2.5 % de cada cola según la F")
        ui.figura(fig, "constructor_f", f"{P}_hist")
    with col_p:
        fig_p = gr.poblaciones([(f"Población 1: {E.pob1.forma.nombre_corto()}", E.pob1.forma.densidad()),
                                (f"Población 2: {E.pob2.forma.nombre_corto()}", E.pob2.forma.densidad())],
                               "Formas de las poblaciones (estandarizadas)", 330)
        ui.figura(fig_p, "constructor_poblaciones", f"{P}_pob")
        if exacta:
            ui.veredicto("<b>Referencia exacta.</b> Las dos poblaciones son normales: por el Teorema 7.3 y la Definición 7.3, "
                         f"F* sigue exactamente una F({g1}, {g2}), sean cuales sean μ y σ.", True)
        else:
            ui.veredicto("<b>La F es solo una referencia aproximada, y puede ser mala.</b> Al menos una población no es "
                         "normal, así que el Teorema 7.3 no aplica y nada garantiza que F* siga una F.", False)

    st.subheader("¿Cumple F* lo que promete la F?")
    filas = []
    for cola in (0.10, 0.05, 0.025, 0.01):
        s = motor.cola_superior(res, cola)
        i = motor.cola_inferior(res, cola)
        filas.append({"cola": f"P(F* > F.{str(cola)[2:]})", "nominal": cola, "empirica": s.estimada, "ee": s.error_estandar})
        filas.append({"cola": f"P(F* < F.{str(1 - cola)[2:]})", "nominal": cola, "empirica": i.estimada, "ee": i.error_estandar})
    df_c = pd.DataFrame(filas)
    cc1, cc2 = st.columns([3, 2])
    with cc1:
        ui.figura(gr.colas(df_c, "Probabilidad en las colas: promesa de la F frente a la simulación"), "constructor_colas", f"{P}_col")
    with cc2:
        mom = pd.DataFrame({
            "Medida": ["Media de F*", "Varianza de F*", "Distancia KS"],
            "Simulación": [float(np.mean(F)), float(np.var(F, ddof=1)), teoria.ks_distancia(F, g1, g2)],
            "F teórica": [teoria.media_f(g2), teoria.varianza_f(g1, g2), 0.0],
        })
        st.dataframe(mom.style.format({"Simulación": "{:.4f}", "F teórica": "{:.4f}"}), hide_index=True,
                     use_container_width=True)
        ui.nota("Media y varianza teóricas: Ejercicio 7.34. La distancia KS es la máxima diferencia vertical entre la "
                "distribución acumulada simulada y la de la F: es casi 0 cuando la F es correcta (complementario).")
    st.markdown(
        "**Cómo leerlo.** Las barras grises son lo que promete la F; las azules, lo que pasó. Con poblaciones normales "
        "coinciden dentro del error de simulación (las líneas negras). Con colas pesadas, las barras azules de las colas son "
        "**más altas**: F* toma valores extremos más seguido de lo que dice la F. Con colas livianas (uniforme) pasa al revés."
    )

with tab_a:
    st.markdown("Así se construye **un** valor de F*: dos muestras, dos varianzas muestrales y un cociente.")
    sem = int(st.number_input("Semilla de este par", 0, 10**6, 7, key=f"{P}_par"))
    y1, y2 = motor.muestras_ejemplo(E, sem)
    ui.figura(gr.muestras_par(y1, y2, "Las dos muestras (cada punto es una observación)"), "constructor_par", f"{P}_mp")
    s1, s2 = y1.var(ddof=1), y2.var(ddof=1)
    st.latex(rf"s_1^2=\frac{{1}}{{{E.n1}-1}}\sum (y_{{1i}}-\bar y_1)^2={s1:.4f},\qquad s_2^2={s2:.4f}")
    st.latex(rf"F^*=\frac{{s_1^2/\sigma_1^2}}{{s_2^2/\sigma_2^2}}=\frac{{{s1:.4f}/{E.pob1.varianza:g}}}{{{s2:.4f}/{E.pob2.varianza:g}}}"
             rf"={(s1 / E.pob1.varianza) / (s2 / E.pob2.varianza):.4f}")
    ui.nota("Cambia la semilla para ver otro par. Cambia μ en la barra lateral: las muestras se desplazan, pero s² y F* no "
            "cambian, porque S² no depende de la media.")

with tab_d:
    t = res.tabla()
    st.dataframe(t.head(2000), use_container_width=True, height=360, hide_index=True)
    ui.tabla_descarga(t, "constructor_replicas", P)
    ui.nota(f"Se muestran las primeras 2000 de {ui.entero(len(t))} réplicas. Tiempo de cálculo: {res.segundos:.2f} s.")
