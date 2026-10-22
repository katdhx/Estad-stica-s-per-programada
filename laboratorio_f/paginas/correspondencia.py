import pandas as pd
import streamlit as st

from nucleo import ui

ui.preparar()
ui.encabezado(
    "Correspondencia con el libro",
    "Qué parte del laboratorio se apoya en qué resultado de los capítulos 7 y 8. Las páginas son las del libro impreso "
    "(en el PDF hay que sumar 24).",
    "Wackerly, Mendenhall y Scheaffer, Estadística matemática con aplicaciones, 7.ª ed.",
)

FILAS = [
    ("Inicio", "Teorema 7.3, Definición 7.3, Ejercicio 8.125", "357, 362, 441", "La cadena del libro y la cobertura real, en vivo."),
    ("Fundamentos", "Ejemplo 8.1, Teorema 7.3, Definición 7.3, Ejemplo 7.7, Ejercicios 7.29, 7.31, 7.33, 7.34, 8.125, Secciones 8.5 y 8.9",
     "357–368, 398, 406, 435, 441", "Enunciados, propiedades y deducciones."),
    ("1. Construye tu F", "Teorema 7.3, Definición 7.3, Ejercicio 7.34", "357, 362, 368",
     "Histograma de F* frente a F(ν₁, ν₂); colas, media y varianza."),
    ("2. Dónde se rompe la cadena", "Ejemplo 8.1, Teorema 7.3, Definición 7.3", "398, 357, 362",
     "E(S²) = σ² siempre; V(S²) y la χ² solo con normalidad; la F hereda el error."),
    ("3. ¿Se cumple lo que promete la F?", "Ejemplo 7.7, Ejercicio 7.27", "363, 367",
     "Probabilidades de S₁²/S₂² con la F y con la simulación; cómo cambian con n."),
    ("4. El intervalo para σ₂²/σ₁²", "Sección 8.5, Ejercicio 8.125, Sección 8.9", "406–407, 441, 435",
     "Cobertura real del intervalo; equivalencia con la probabilidad central de F*."),
    ("5. Mapa de robustez", "Teorema 7.3, Ejercicio 8.125", "357, 441",
     "La cobertura ordenada por la curtosis; mapa de calor de parejas de formas."),
    ("6. Experimentos guiados", "Ejemplo 8.1, Teorema 7.3, Definición 7.3", "398, 357, 362",
     "Media, asimetría frente a colas, una sola población no normal, n grande, colas livianas, casi normal."),
    ("Calculadora", "Ejemplo 7.7, Ejercicios 7.27, 7.29, 7.36, 8.125, 8.126", "363, 367–368, 441",
     "Cuantiles, probabilidades e intervalos paso a paso."),
    ("Poblaciones", "Secciones 4.4, 4.5, 4.6; Ejercicios 4.182–4.183; Definición 7.2", "—",
     "Uniforme, normal, exponencial y gamma, log-normal y t, todas con media 0 y varianza 1 antes de escalar."),
]
df = pd.DataFrame(FILAS, columns=["Parte del laboratorio", "Resultado del libro", "Páginas", "Qué se hace"])
st.dataframe(df, hide_index=True, use_container_width=True, height=420)
ui.tabla_descarga(df, "correspondencia", "corr")

st.subheader("Lo que es complementario (no está en los capítulos 7 y 8)")
st.markdown(
    "- La **curtosis en exceso** κ y la **asimetría** como medidas de la forma de una población.\n"
    "- La fórmula **V(S²) = σ⁴[2/(n−1) + κ/n]**, que se deduce con los valores esperados del capítulo 5.\n"
    "- La **cobertura límite** 2Φ(z_{α/2}·√(2/(2+κ))) − 1 y su versión para n finito.\n"
    "- La **distancia de Kolmogorov** (KS) entre la distribución simulada y la F.\n\n"
    "Estas herramientas se usan para explicar lo que muestra la simulación, nunca para reemplazar a los resultados del libro."
)
