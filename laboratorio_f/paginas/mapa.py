import numpy as np
import streamlit as st

from nucleo import graficos as gr
from nucleo import motor, teoria, ui
from nucleo.poblaciones import CATALOGO_ROBUSTEZ, forma

P = "map"
ui.preparar()
ui.encabezado(
    "5. Mapa de robustez",
    "¿Qué característica de la población decide cuánto falla la F? Se prueban muchas distribuciones distintas "
    "(simétricas, asimétricas, de colas livianas y pesadas) y se ordenan por su curtosis. El resultado es un patrón muy limpio.",
    "Teorema 7.3 (p. 357), Ejercicio 8.125 (p. 441) y Sección 8.9 (p. 435). La curtosis y la curva teórica son complementarias.",
)

st.sidebar.header("Parámetros")
n = int(st.sidebar.select_slider("Tamaño de cada muestra (n₁ = n₂)", [10, 20, 50, 100, 200, 500], 100, key=f"{P}_n"))
B = int(st.sidebar.number_input("Pares de muestras por distribución", 1000, 50000, 6000, 1000, key=f"{P}_B"))
conf = float(st.sidebar.number_input("Confianza (%)", 50.0, 99.9, 95.0, 0.5, key=f"{P}_conf"))
alfa = 1 - conf / 100

t_curt, t_parejas = st.tabs(["Todo depende de las colas", "Parejas de formas"])

with t_curt:
    st.markdown(f"Se simulan {len(CATALOGO_ROBUSTEZ)} distribuciones, cada una usada en las dos poblaciones con la misma varianza. "
                "El eje horizontal es la curtosis en exceso κ: 0 para la normal, negativa para colas livianas y positiva para "
                "colas pesadas.")
    if st.button("Simular las distribuciones", type="primary", key=f"{P}_b1"):
        b, av = ui.barra("Simulando cada distribución…")
        df = ui.cacheado(("mapa", n, B, alfa), lambda: motor.barrido_formas(CATALOGO_ROBUSTEZ, n, B, alfa, 2026, av))
        b.empty()
        st.session_state[f"{P}_r1"] = (df, n, alfa)
    if f"{P}_r1" in st.session_state:
        df, n_, a_ = st.session_state[f"{P}_r1"]
        ks = np.linspace(-1.3, max(12.0, float(df["curtosis"].max()) + 1), 300)
        curva = (ks, np.array([teoria.cobertura_limite(k, a_) for k in ks]))
        ui.figura(gr.mapa_robustez(df, 1 - a_, curva, n_, "Cobertura real del intervalo para σ₂²/σ₁² según la curtosis"),
                  "mapa_robustez", f"{P}_m")
        ui.veredicto(
            "<b>El patrón que se descubre.</b> Los puntos casi no dependen de que la distribución sea simétrica o asimétrica: "
            "se ordenan por la curtosis y caen cerca de una sola curva. La normal (κ = 0) es el único punto exactamente en "
            "el nivel prometido. A la izquierda (colas livianas) los intervalos aciertan de más; a la derecha (colas pesadas) "
            "aciertan cada vez menos. Por ejemplo, la t con 7 gl (simétrica) y la gamma con α = 3 (asimétrica) son muy distintas, "
            "pero las dos tienen κ = 2 y fallan casi igual; lo mismo la t con 10 gl y la gamma con α = 6 (κ = 1).")
        ui.nota("La curva discontinua es 2Φ(z·√(2/(2+κ))) − 1, el límite para n grande que sale de V(S²) = σ⁴[2/(n−1) + κ/n] "
                "(complementario). Con n pequeño los puntos quedan un poco por encima de la curva. La t con pocos grados de "
                "libertad también queda algo por encima: su curtosis viene de valores extremos muy raros, que con n moderado "
                "casi nunca aparecen. Pasa el cursor por los puntos sin rótulo para ver cuál es.")
        st.dataframe(df[["forma", "familia", "curtosis", "asimetria", "cobertura", "ee"]].sort_values("curtosis")
                     .style.format({"curtosis": "{:.2f}", "asimetria": "{:.2f}", "cobertura": "{:.4f}", "ee": "{:.4f}"}),
                     hide_index=True, use_container_width=True, height=36 * (len(df) + 1) + 4)
        ui.tabla_descarga(df, "mapa_robustez", f"{P}_t1")

with t_parejas:
    st.markdown("¿Qué pasa si **solo una** de las poblaciones no es normal, o si son de formas distintas? Cada casilla es la "
                "cobertura real del intervalo del " + f"{conf:g} % con esa pareja de formas (n₁ = n₂ = {n}).")
    formas = [forma("uniforme"), forma("normal"), forma("t", 10.0), forma("gamma", 2.0), forma("t", 5.0),
              forma("exponencial"), forma("lognormal", 0.5)]
    Bp = int(st.number_input("Pares de muestras por casilla", 500, 20000, 3000, 500, key=f"{P}_Bp"))
    if st.button(f"Simular las {len(formas) ** 2} parejas", type="primary", key=f"{P}_b2"):
        b, av = ui.barra("Simulando cada pareja…")
        dfp = ui.cacheado(("parejas", n, Bp, alfa), lambda: motor.barrido_parejas(formas, n, Bp, alfa, 2026, av))
        b.empty()
        st.session_state[f"{P}_r2"] = (dfp, alfa)
    if f"{P}_r2" in st.session_state:
        dfp, a_ = st.session_state[f"{P}_r2"]
        ui.figura(gr.mapa_calor(dfp, 1 - a_, "Cobertura real según las formas de las dos poblaciones"), "mapa_parejas", f"{P}_hm")
        ui.veredicto("<b>Lectura.</b> Solo la casilla normal–normal está garantizada. Basta con que <b>una</b> de las dos "
                     "poblaciones tenga colas pesadas para que la cobertura caiga: el error de esa población se transmite al "
                     "cociente. Los colores más oscuros (petróleo) son coberturas altas; los naranjas, coberturas bajas.")
        ui.tabla_descarga(dfp, "mapa_parejas", f"{P}_t2")
