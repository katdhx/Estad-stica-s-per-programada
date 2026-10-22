import streamlit as st

from lab import graficos as gr
from lab import motor, ui
from lab.poblaciones import crear

ui.preparar()

st.title("Laboratorio de intervalos de confianza")
st.markdown(
    '<p class="lab-pregunta">Un intervalo de confianza es una regla que convierte una muestra en dos números. '
    "Como la muestra es aleatoria, el intervalo también lo es. Este laboratorio repite el muestreo miles de veces "
    "para ver, con números, lo que los capítulos 7 y 8 de Wackerly, Mendenhall y Scheaffer demuestran con teoremas.</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- Figura 8.8
st.header("La Figura 8.8, en vivo")
st.markdown(
    "En la página 414 el libro muestra 24 experimentos binomiales con $n = 35$ y $p = 0.5$. Cada uno produce el "
    r"intervalo $\hat p \pm 1.96\sqrt{\hat p(1-\hat p)/35}$, y 23 de los 24 contienen a $p$. "
    "Aquí puedes generar tus propias tandas de 24."
)
if "inicio_tanda" not in st.session_state:
    st.session_state.inicio_tanda = 0
c1, c2 = st.columns([1, 4])
with c1:
    if st.button("Generar otra tanda", type="primary"):
        st.session_state.inicio_tanda += 1
    st.caption(f"Tanda número {st.session_state.inicio_tanda + 1}.")
esc = motor.Escenario("proporcion_wald", crear("bernoulli", p=0.5), n1=35, B=24, alfa=0.05,
                      semilla=814 + st.session_state.inicio_tanda)
res = ui.simular_cache(esc)
cob = res.cobertura()
with c1:
    st.metric("Intervalos que contienen p", f"{cob.aciertos} de {cob.B}")
with c2:
    fig = gr.intervalos_apilados(res.tabla, 0.5, "p")
    fig.update_layout(height=430)
    ui.mostrar_figura(fig, "figura_8_8_en_vivo", "inicio")

# ---------------------------------------------------------------- n frente a B
st.header("Dos números que no hay que confundir")
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        r"""
**$n$: el tamaño de cada muestra.** Es el número de observaciones $Y_1,\dots,Y_n$ con las que se calcula
**un** intervalo. Al crecer $n$, el intervalo se vuelve más estrecho porque el error estándar
$\sigma/\sqrt n$ disminuye.

Una muestra de 100 000 observaciones da **un solo intervalo**, muy angosto. Ese intervalo contiene
o no contiene al parámetro: con una sola muestra no se puede medir la cobertura.
"""
    )
with c2:
    st.markdown(
        r"""
**$B$: el número de muestras.** Es cuántas veces repetimos el experimento completo. Cada repetición
produce un intervalo nuevo, y la fracción de intervalos que contienen al parámetro estima el
**coeficiente de confianza**, que el libro define en el muestreo repetido (Sección 8.5, p. 406).

100 000 muestras dan **cien mil intervalos**. Con ellos, la cobertura se estima con un error estándar
de $\sqrt{0.95\cdot 0.05/100\,000}\approx 0.0007$.
"""
    )
ui.nota("El costo de una simulación es proporcional a n × B. El motor procesa las muestras por lotes de a lo sumo "
        "cuatro millones de números (unos 32 MB), así que n = 100 000 con B = 1000 no satura la memoria.")

# ---------------------------------------------------------------- recorrido
st.header("Recorrido sugerido para la sustentación")
recorrido = [
    ("Fundamentos", "Los teoremas del capítulo 7 y el método del pivote de la Sección 8.5, con cada procedimiento en su ficha."),
    ("1. Construcción de intervalos", "¿Qué significa «95 % de confianza»? Muchos intervalos, uno por muestra, y cuáles fallan."),
    ("2. Tamaño muestral", "¿Por qué la amplitud cae como 1/√n? Desde n = 5 hasta n = 100 000."),
    ("3. Cobertura", "¿La cobertura simulada coincide con la nominal? ¿Cuánto error tiene la propia simulación?"),
    ("4. Nivel de confianza", "90, 95 y 99 % sobre las mismas muestras: el precio de la confianza se paga en amplitud."),
    ("5. Distribuciones muestrales", "Los Teoremas 7.1 y 7.3, la Definición 7.2 y el TCL, vistos como histogramas."),
    ("6. Supuestos", "Qué pasa cuando no se cumplen: χ² con poblaciones no normales, Wald cerca de 0 o 1, varianzas distintas."),
    ("Calculadora", "Los Ejemplos 8.4, 8.7, 8.8, 8.11, 8.12 y 8.13 del libro, reproducidos paso a paso."),
]
for nombre, desc in recorrido:
    st.markdown(f"**{nombre}.** {desc}")

st.header("Demostración y simulación no son lo mismo")
st.markdown(
    "Un teorema, como el Teorema 7.3, establece un resultado **para todo n** y para toda muestra posible. "
    "Una simulación solo **ilustra y comprueba empíricamente** ese resultado para los valores concretos que elegimos, "
    "con un error de Monte Carlo que podemos cuantificar. La simulación no demuestra nada, pero sí puede refutar: "
    "si la cobertura simulada del intervalo χ² con una población exponencial es 70 %, eso basta para concluir que el "
    "procedimiento no tiene coeficiente 95 % fuera de la normalidad, que es justo lo que advierte la Sección 8.9."
)
