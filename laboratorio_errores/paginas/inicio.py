import streamlit as st

from nucleo import binomial as bn
from nucleo import ui
from nucleo.ui import ALFA, BETA, NAVY, POTENCIA

ui.preparar()
ui.encabezado(
    "El costo de equivocarse: errores tipo I y tipo II",
    "Una prueba estadística es una regla para decidir con datos incompletos. Por eso se puede equivocar de "
    "dos maneras distintas. Este laboratorio mide cuánto cuesta cada equivocación y qué pasa con ese costo "
    "cuando cambiamos la regla o el tamaño de la muestra.",
    "Wackerly, Mendenhall y Scheaffer, <i>Estadística matemática con aplicaciones</i>, 7.ª ed., capítulo 10: "
    "Sección 10.1 (Introducción), Sección 10.2 (Elementos de una prueba estadística) y conexión con la "
    "Sección 10.4 (probabilidades de error tipo II y tamaño muestral para pruebas Z).")

st.header("Los cuatro elementos de una prueba (Sección 10.2)")
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        "1. **Hipótesis nula** $H_0$: la afirmación que se pone a prueba (por ejemplo $p = 0.5$).\n"
        "2. **Hipótesis alternativa** $H_a$: lo que se quiere mostrar con los datos (por ejemplo $p < 0.5$).\n"
        "3. **Estadístico de prueba**: una función de la muestra con la que se decide (en el ejemplo de Jones, "
        "$Y$ = número de votantes a favor).\n"
        "4. **Región de rechazo** $RR$: los valores del estadístico con los que se rechaza $H_0$ "
        "(en el ejemplo, $RR = \\{y \\le 2\\}$).")
with c2:
    st.markdown("Con esa regla solo hay cuatro situaciones posibles:")
    st.markdown(f"""
| | **$H_0$ es verdadera** | **$H_a$ es verdadera** |
|---|---|---|
| **Rechazar $H_0$** | {ui.etiqueta("Error tipo I", ALFA)} probabilidad $\\alpha$ | {ui.etiqueta("Correcto", POTENCIA)} probabilidad = potencia |
| **No rechazar $H_0$** | {ui.etiqueta("Correcto", NAVY)} probabilidad $1-\\alpha$ | {ui.etiqueta("Error tipo II", BETA)} probabilidad $\\beta$ |
""", unsafe_allow_html=True)

st.header("Las definiciones")
st.markdown(
    "- **Error tipo I**: rechazar $H_0$ cuando $H_0$ es verdadera. Su probabilidad se denota $\\alpha$ y se "
    "llama **nivel** (o nivel de significancia) de la prueba.\n"
    "- **Error tipo II**: no rechazar $H_0$ cuando $H_a$ es verdadera. Su probabilidad se denota $\\beta$.\n"
    "- **Potencia** en un valor de la alternativa: $1 - \\beta$, la probabilidad de rechazar $H_0$ cuando ese "
    "valor de $H_a$ es el verdadero.")
st.latex(r"\alpha = P(\text{estadístico} \in RR \mid H_0 \text{ verdadera}), \qquad "
         r"\beta = P(\text{estadístico} \notin RR \mid H_a \text{ verdadera})")

ui.caja(
    "<b>Ojo con la alternativa compuesta.</b> Hₐ: p &lt; 0.5 contiene infinitos valores de p. "
    "Por eso β no es un número sino una función: hay un β(p) distinto para cada valor de la alternativa. "
    "El libro calcula β en un valor <i>específico</i>, p = 0.3; la curva del Módulo 1 muestra el resto.")

a, b = bn.alfa(15, 0.5, 2), bn.beta(15, 0.3, 2)
st.header("El caso del libro en una línea")
ui.cifras([
    ("α = P(Y ≤ 2 | p = 0.5)", ui.fmt(a, 5), "Binomial(15, 0.5)", ALFA),
    ("β(0.3) = P(Y > 2 | p = 0.3)", ui.fmt(b, 3), "Binomial(15, 0.3)", BETA),
    ("Potencia en p = 0.3", ui.fmt(1 - b, 3), "1 − β(0.3)", POTENCIA),
])
st.markdown(
    "La regla del libro casi nunca acusa sin razón (α ≈ 0.004), pero a cambio deja pasar la mayoría de las "
    "veces en que Jones sí va perdiendo con p = 0.3 (β ≈ 0.873). **Ese es el costo de equivocarse**: "
    "bajar un error sube el otro, a menos que se aumente el tamaño de la muestra.")

st.header("Ruta de la exposición")
st.markdown(
    "1. **El ejemplo de Jones**: α, β y potencia exactos con la binomial; mover el umbral y ver el intercambio.\n"
    "2. **El dilema entre α y β**: la misma idea con la prueba Z y las dos campanas superpuestas; tamaño "
    "muestral (Sección 10.4) y exportación JSON para la segunda aplicación.\n"
    "3. **Monte Carlo**: repetir la prueba miles de veces y contar los errores de verdad.\n"
    "4. **Toma una decisión**: el público decide y la app revela si se equivocó.\n"
    "5. **Excel**: el profesor comprueba todo con fórmulas de Excel y se pueden traer datos reales.")
