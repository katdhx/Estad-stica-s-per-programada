import pandas as pd
import streamlit as st

from lab import ui
from lab.correspondencia import FILAS, PROCEDIMIENTOS_LIBRO

ui.preparar()
ui.encabezado(
    "Correspondencia con el libro",
    "Qué parte de la aplicación ilustra qué resultado de los capítulos 7 y 8. Las páginas son las del libro impreso.",
    "Wackerly, Mendenhall y Scheaffer, Estadística matemática con aplicaciones, 7.ª ed., caps. 7 y 8.",
)

st.subheader("Módulos de la aplicación")
df = pd.DataFrame(FILAS, columns=["Módulo", "Archivo", "Resultado del libro", "Sección", "Página", "Qué se comprueba"])
st.dataframe(df, hide_index=True, use_container_width=True, height=min(900, 38 * len(df) + 40))
ui.descargar_tabla(df, "correspondencia_modulos", "corr1")

st.subheader("Procedimientos de intervalos de confianza")
dp = pd.DataFrame(PROCEDIMIENTOS_LIBRO, columns=["Procedimiento", "Sección", "Ejemplos", "Se apoya en", "Tipo"])
st.dataframe(dp, hide_index=True, use_container_width=True)
ui.descargar_tabla(dp, "correspondencia_procedimientos", "corr2")

st.subheader("Qué no está en los capítulos 7 y 8 y por eso no se incluyó")
st.markdown(
    "- Intervalo de Welch para μ₁ − μ₂ con varianzas distintas.\n"
    "- Intervalos de Wilson, de Agresti–Coull o exactos de Clopper–Pearson para p.\n"
    "- Intervalos bootstrap.\n\n"
    "Las afirmaciones que el laboratorio añade por su cuenta, como E(S) = σ·c4(n), la cobertura exacta del intervalo de Wald, "
    "el límite de la cobertura χ² en función de la curtosis o la aproximación para la t agrupada, se identifican siempre como "
    "**complementarias** y se derivan de resultados del curso. No se atribuyen al libro."
)
st.subheader("Errata del libro detectada")
st.markdown(
    "- **Ejemplo 8.7 (p. 413).** El intervalo es del 90 % (usa z.05 = 1.645, y el propio texto dice «aproximadamente 90 % de "
    "todos los intervalos»), pero la última frase dice «captan la media real en aproximadamente 95 %». Debe leerse 90 %."
)
