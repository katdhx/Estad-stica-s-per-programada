import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nucleo import graficos as gr
from nucleo import motor, ui
from nucleo.poblaciones import Poblacion, forma

P = "des"
ui.preparar()
ui.encabezado(
    "6. Experimentos guiados",
    "Seis preguntas para descubrir los patrones. Primero elige qué crees que va a pasar, después pulsa «Comprobar». "
    "Todas miden lo mismo: la cobertura real del intervalo del 95 % para σ₂²/σ₁², que es la probabilidad de que F* caiga "
    "en el 95 % central de la F.",
    "Teorema 7.3, Definición 7.3, Ejercicio 8.125. La curtosis es complementaria.",
)

B = 20000
NORMAL, EXPO = forma("normal"), forma("exponencial")

EXPERIMENTOS = [
    {
        "clave": "media",
        "titulo": "¿Importa la media de las poblaciones?",
        "pregunta": "Si a la población 1 le sumo 50 (cambio μ₁ de 0 a 50), ¿qué le pasa a la cobertura?",
        "opciones": ["Baja mucho", "Sube", "No cambia nada"],
        "correcta": "No cambia nada",
        "escenarios": [("μ₁ = 0", Poblacion(NORMAL, 1, 0), Poblacion(NORMAL), 10, 10),
                       ("μ₁ = 50", Poblacion(NORMAL, 1, 50), Poblacion(NORMAL), 10, 10)],
        "explicacion": "S² mide la dispersión alrededor de la propia media muestral: si a todos los datos se les suma 50, "
                       "cada Yᵢ − Ȳ queda igual. Por eso S², F* y el intervalo son <b>idénticos</b>: con la misma semilla, "
                       "las dos coberturas coinciden. La F compara varianzas, no medias.",
    },
    {
        "clave": "asimetria",
        "titulo": "¿Qué importa más: la asimetría o las colas?",
        "pregunta": "La t con 7 gl es simétrica y la gamma con α = 3 es asimétrica, pero las dos tienen la misma curtosis "
                    "(κ = 2). ¿Cuál falla más?",
        "opciones": ["La gamma, porque es asimétrica", "La t, porque tiene colas pesadas", "Fallan casi igual"],
        "correcta": "Fallan casi igual",
        "escenarios": [("Normal (κ = 0)", Poblacion(NORMAL), Poblacion(NORMAL), 50, 50),
                       ("t con 7 gl (κ = 2, simétrica)", Poblacion(forma("t", 7.0)), Poblacion(forma("t", 7.0)), 50, 50),
                       ("Gamma α = 3 (κ = 2, asimétrica)", Poblacion(forma("gamma", 3.0)), Poblacion(forma("gamma", 3.0)), 50, 50)],
        "explicacion": "Para la varianza muestral lo decisivo es el cuarto momento: V(S²) = σ⁴[2/(n−1) + κ/n]. Dos "
                       "poblaciones con la misma curtosis hacen variar a S² casi lo mismo, aunque una sea simétrica y la otra no. "
                       "Por eso fallan casi igual. La asimetría importa mucho para la media (la t del capítulo 8), pero poco aquí.",
    },
    {
        "clave": "una",
        "titulo": "¿Basta con que una sola población no sea normal?",
        "pregunta": "Si la población 1 es normal y solo la población 2 es exponencial, ¿la cobertura…?",
        "opciones": ["Se mantiene en 95 %", "Cae, pero menos que con las dos exponenciales", "Cae igual que con las dos exponenciales"],
        "correcta": "Cae, pero menos que con las dos exponenciales",
        "escenarios": [("Normal y normal", Poblacion(NORMAL), Poblacion(NORMAL), 30, 30),
                       ("Normal y exponencial", Poblacion(NORMAL), Poblacion(EXPO), 30, 30),
                       ("Exponencial y exponencial", Poblacion(EXPO), Poblacion(EXPO), 30, 30)],
        "explicacion": "F* depende de las dos varianzas muestrales. La de la población normal se comporta como dice la χ²; la de "
                       "la exponencial varía de más. El exceso de variabilidad de una sola población basta para ensanchar la "
                       "distribución de F* y romper la cobertura. Con las dos poblaciones no normales, el efecto se suma.",
    },
    {
        "clave": "n",
        "titulo": "¿Más datos lo arreglan?",
        "pregunta": "Con poblaciones exponenciales, ¿qué pasa con la cobertura si paso de n = 10 a n = 1000?",
        "opciones": ["Sube hasta 95 %", "Se queda lejos de 95 %", "Baja a cero"],
        "correcta": "Se queda lejos de 95 %",
        "escenarios": [("n = 10", Poblacion(EXPO), Poblacion(EXPO), 10, 10),
                       ("n = 100", Poblacion(EXPO), Poblacion(EXPO), 100, 100),
                       ("n = 1000", Poblacion(EXPO), Poblacion(EXPO), 1000, 1000)],
        "explicacion": "Con la media, el TCL arregla la falta de normalidad. Aquí no: los dos términos de V(S²) = σ⁴[2/(n−1) + κ/n] "
                       "bajan al mismo ritmo, así que la proporción entre la variabilidad real y la que supone la χ² no cambia con n. "
                       "La cobertura se estanca cerca de 2Φ(0.98) − 1 ≈ 67 %.",
    },
    {
        "clave": "livianas",
        "titulo": "¿Y si las colas son livianas?",
        "pregunta": "Con poblaciones uniformes (sin colas, κ = −1.2), ¿la cobertura del intervalo del 95 % es…?",
        "opciones": ["Menor que 95 %", "Mayor que 95 %", "Exactamente 95 %"],
        "correcta": "Mayor que 95 %",
        "escenarios": [("Normal", Poblacion(NORMAL), Poblacion(NORMAL), 30, 30),
                       ("Uniforme", Poblacion(forma("uniforme")), Poblacion(forma("uniforme")), 30, 30)],
        "explicacion": "Con κ < 0, S² varía <b>menos</b> de lo que supone la χ²; los intervalos construidos con la F son más anchos "
                       "de lo necesario y aciertan de más. Suena bien, pero también es un error: el «95 %» ya no significa 95 %, "
                       "y se pierde precisión.",
    },
    {
        "clave": "casi",
        "titulo": "¿Casi normal es casi exacto?",
        "pregunta": "Una gamma con α = 50 se parece mucho a una normal (κ = 0.12). ¿Cuánto se aleja su cobertura del 95 %?",
        "opciones": ["Muy poco", "Tanto como la exponencial", "Nada: es exacta"],
        "correcta": "Muy poco",
        "escenarios": [("Normal", Poblacion(NORMAL), Poblacion(NORMAL), 50, 50),
                       ("Gamma α = 50", Poblacion(forma("gamma", 50.0)), Poblacion(forma("gamma", 50.0)), 50, 50),
                       ("Exponencial (gamma α = 1)", Poblacion(EXPO), Poblacion(EXPO), 50, 50)],
        "explicacion": "El error crece con la curtosis de forma continua: una población casi normal (κ cercano a 0) da una "
                       "cobertura casi correcta, pero no exacta. Exacta solo es la normal. En la práctica, la pregunta no es "
                       "«¿es normal?», sino «¿qué tan pesadas son sus colas?».",
    },
]

for exp in EXPERIMENTOS:
    st.header(exp["titulo"])
    st.markdown(exp["pregunta"])
    c1, c2 = st.columns([2, 1])
    pred = c1.radio("Mi predicción", exp["opciones"], index=None, horizontal=True, key=f"{P}_{exp['clave']}_pred")
    if c2.button("Comprobar", type="primary", key=f"{P}_{exp['clave']}_btn", disabled=pred is None,
                 use_container_width=True):
        filas = []
        for nombre, p1, p2, n1, n2 in exp["escenarios"]:
            res = ui.simular(motor.Escenario(p1, p2, n1, n2, B, 2026))
            c = motor.cobertura(res, 0.05)
            filas.append({"Escenario": nombre, "Cobertura real": c.estimada, "ee": c.error_estandar})
        st.session_state[f"{P}_{exp['clave']}_res"] = (pd.DataFrame(filas), pred)
    if f"{P}_{exp['clave']}_res" in st.session_state:
        df, pred_guardada = st.session_state[f"{P}_{exp['clave']}_res"]
        fig = go.Figure(go.Bar(
            x=df["Cobertura real"], y=df["Escenario"], orientation="h",
            marker=dict(color=[gr.TINTA if abs(v - 0.95) < 2.5 * e else (gr.NARANJA if v < 0.95 else gr.AQUA)
                               for v, e in zip(df["Cobertura real"], df["ee"])], line=dict(color="white", width=2)),
            error_x=dict(type="data", array=1.96 * df["ee"], color=gr.GRAFITO, thickness=1.2),
            text=[f"{100 * v:.1f} %" for v in df["Cobertura real"]], textposition="inside", insidetextanchor="end",
            textfont=dict(color="white", size=13), hovertemplate="%{y}<br>%{x:.4f}<extra></extra>"))
        fig.add_vline(x=0.95, line=dict(color=gr.TINTA, width=1.5, dash="dot"), annotation_text="prometido 95 %",
                      annotation_position="top")
        gr.base(fig, None, 120 + 60 * len(df), x="Cobertura real del intervalo del 95 %")
        fig.update_layout(showlegend=False, margin=dict(l=230, b=60, t=30))
        fig.update_xaxes(range=[min(0.5, float(df["Cobertura real"].min()) - 0.05), 1.0])
        fig.update_yaxes(autorange="reversed", showgrid=False)
        st.plotly_chart(fig, use_container_width=True, config=gr.CONFIG, key=f"{P}_{exp['clave']}_fig")
        acierto = pred_guardada == exp["correcta"]
        ui.veredicto(("<b>¡Acertaste!</b> " if acierto else f"<b>La respuesta es: «{exp['correcta']}».</b> ") + exp["explicacion"],
                     acierto)
    st.divider()

ui.nota(f"Cada barra usa {ui.entero(B)} pares de muestras; las líneas grises son ±1.96 errores estándar de la simulación.")
