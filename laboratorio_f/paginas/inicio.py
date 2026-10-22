import streamlit as st

from nucleo import fdist, graficos as gr
from nucleo import motor, teoria, ui
from nucleo.poblaciones import Poblacion, forma

ui.preparar()

st.title("La normalidad y la distribución F")
st.markdown(
    '<p class="f-pregunta">Cuando comparamos las varianzas de dos poblaciones, el libro usa la distribución F. '
    "Pero la F solo es la distribución correcta si las dos poblaciones son <b>normales</b>. "
    "Aquí puedes cambiar la forma de las poblaciones y ver, en vivo, qué parte de la teoría se rompe y cuánto.</p>",
    unsafe_allow_html=True,
)

OPCIONES = {
    "Normal": forma("normal"),
    "Uniforme (colas livianas)": forma("uniforme"),
    "t con 5 gl (colas pesadas)": forma("t", 5.0),
    "Exponencial (asimétrica)": forma("exponencial"),
    "Log-normal (muy asimétrica)": forma("lognormal", 0.5),
}
c1, c2 = st.columns([3, 2])
with c1:
    eleccion = st.radio("Forma de las dos poblaciones", list(OPCIONES), horizontal=True, key="ini_forma")
with c2:
    n = st.select_slider("Tamaño de cada muestra (n₁ = n₂)", [5, 10, 20, 50, 100, 300], 10, key="ini_n")
f = OPCIONES[eleccion]
esc = motor.Escenario(Poblacion(f), Poblacion(f), n, n, 20000, 2026)
res = ui.simular(esc)
cob = motor.cobertura(res, 0.05)

ui.cadena(f, f, cob.estimada, 0.95)

g, d = st.columns([5, 2])
with g:
    a, b = fdist.intervalo_central(0.05, n, n)
    fig = gr.histograma_f(res.F_pivote, n - 1, n - 1,
                          f"F* = (S₁²/σ₁²)/(S₂²/σ₂²) en 20 000 pares de muestras, n = {n}",
                          region=(a, b), exacta=f.es_normal, x="F*", alto=430,
                          etiqueta_region="2.5 % de cada cola según la F")
    ui.figura(fig, "inicio_f", "ini")
with d:
    fuera = 1 - cob.estimada
    ui.cifra(f"{100 * cob.estimada:.1f} %", "de los intervalos del 95 % para σ₂²/σ₁² contuvieron el valor verdadero",
             alerta=not cob.compatible())
    st.markdown("")
    if f.es_normal:
        ui.veredicto(f"<b>La F es exacta.</b> El histograma sigue la curva y {100 * fuera:.1f} % de los valores cae en "
                     "las colas naranjas, igual al 5 % que promete la F (salvo ±0.3 % de error de simulación).", True)
    else:
        lim = teoria.cobertura_limite(f.curtosis(), 0.05)
        ui.veredicto(f"<b>La F deja de ser la referencia.</b> Cae {100 * fuera:.1f} % de los valores en las colas "
                     f"naranjas, no 5 %. Y no se arregla con más datos: con n muy grande la cobertura tiende a "
                     f"{100 * lim:.0f} %.", False)
    ui.nota("Prueba a mover n: con la normal nada cambia; con las demás, a veces empeora.")

st.header("Qué hay en el laboratorio")
for nombre, desc in [
    ("Fundamentos", "Teorema 7.3, Definición 7.3, propiedades de la F, el Ejemplo 7.7 y el intervalo del Ejercicio 8.125."),
    ("1. Construye tu F", "Eliges dos poblaciones, sus σ y sus n, y comparas el histograma del estadístico con la F teórica."),
    ("2. Dónde se rompe la cadena", "Eslabón por eslabón: S², la χ², la varianza de S² y la F. Ahí se ve dónde falla."),
    ("3. ¿Se cumple lo que promete la F?", "Las probabilidades de cola del Ejemplo 7.7, medidas de verdad, y cómo cambian con n."),
    ("4. El intervalo para σ₂²/σ₁²", "El intervalo del capítulo 8, dibujado réplica por réplica, y su cobertura real."),
    ("5. Mapa de robustez", "Catorce distribuciones sobre una sola curva, y un mapa de calor con todas las parejas."),
    ("6. Experimentos guiados", "Seis preguntas para predecir primero y comprobar después."),
]:
    st.markdown(f"**{nombre}.** {desc}")
