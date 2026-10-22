import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from lab import graficos as gr
from lab import intervalos as ic
from lab import motor, ui

P = "e4"
ui.preparar()
ui.encabezado(
    "Experimento 4. Nivel de confianza",
    "¿Qué se gana y qué se pierde al pasar del 90 % al 99 %? Se usan exactamente las mismas muestras con tres niveles "
    "distintos, de modo que la única diferencia es el valor crítico.",
    "Sección 8.6 (Ejemplo 8.6, Figura 8.7), Sección 8.8 (Figura 8.10), Sección 8.9 (Figura 8.11), Tablas 4, 5 y 6 del Apéndice 3.",
)

esc, errores = ui.selector_escenario(P, n_defecto=25, B_defecto=2000, B_max=50000, permitir_lado=False,
                                     mostrar_nivel=False, proc_defecto="media_t")
st.sidebar.subheader("Niveles")
niveles = st.sidebar.multiselect("Niveles de confianza (%)", [80.0, 90.0, 95.0, 98.0, 99.0, 99.9],
                                 default=[90.0, 95.0, 99.0], key=f"{P}_niv")
niveles = sorted(niveles)[:3]
if len(niveles) == 0:
    errores = errores + ["Elige al menos un nivel de confianza."]
ui.costo(esc)
bloqueado = ui.mostrar_errores(errores)
firma = (esc, tuple(niveles))
if ui.boton_ejecutar(P, bloqueado):
    barra, avance = ui.barra_progreso()
    res = ui.simular_cache(esc, avance)
    barra.empty()
    ui.guardar(P, firma, res)

res, viejo = ui.recuperar(P, firma)
if res is None:
    st.info("Pulsa «Ejecutar simulación». Se usan las mismas B muestras para todos los niveles elegidos (hasta tres).")
    st.stop()
if viejo:
    ui.aviso_desactualizado()
E = res.escenario
niv_guardados = st.session_state[f"{P}_resultado"][0][1]
tablas = {}
filas = []
for nv in niv_guardados:
    a = 1 - nv / 100
    t = motor.calcular_intervalos(E, res.estadisticos, alfa=a, lado="bilateral")
    tablas[f"{nv:g} %"] = t
    cb = motor.resumen_cobertura(t["cubre"].to_numpy(), 1 - a)
    if E.procedimiento == "media_t":
        crit, nombre = ic.t_critico(a / 2, E.n1 - 1), f"t_{{α/2,{E.n1 - 1}}}"
    elif E.procedimiento in ("varianza_chi2", "exponencial_chi2", "razon_varianzas_f"):
        crit, nombre = np.nan, "—"
    elif E.procedimiento == "dif_medias_t":
        crit, nombre = ic.t_critico(a / 2, E.n1 + E.n2 - 2), "t_{α/2}"
    else:
        crit, nombre = ic.z_critico(a / 2), "z_{α/2}"
    filas.append({"nivel": f"{nv:g} %", "α": a, "valor crítico": crit, "amplitud media": t["amplitud"].mean(),
                  "cobertura empírica": cb.estimada, "ee Monte Carlo": cb.error_estandar})
df = pd.DataFrame(filas)
ref = df["amplitud media"].iloc[len(df) // 2]
df["amplitud relativa"] = df["amplitud media"] / ref

pres, fund, datos = st.tabs(["Resultados", "Fundamentación matemática", "Datos"])
with pres:
    cols = st.columns(len(df))
    for c, (_, f) in zip(cols, df.iterrows()):
        c.metric(f"Nivel {f['nivel']}", f"cobertura {f['cobertura empírica']:.4f}",
                 help=f"Amplitud media {f['amplitud media']:.4f}")
        c.caption(f"Amplitud media {f['amplitud media']:.4f}, es decir, {f['amplitud relativa']:.3f} veces la del nivel central.")
    k = st.slider("Muestras a mostrar", 5, 60, 25, key=f"{P}_k")
    ui.mostrar_figura(gr.niveles_anidados(tablas, res.theta, ui.SIMBOLO[E.procedimiento], k,
                                          "Los mismos datos, tres niveles de confianza"), "experimento4_anidados", f"{P}_anid")
    ui.nota("Para cada muestra, los tres intervalos tienen el mismo centro (en Z y t) y están anidados: el del 99 % contiene "
            "al del 95 %, que contiene al del 90 %. Por eso, si el del 99 % falla, también fallan los otros dos.")
    cA, cB = st.columns(2)
    with cA:
        ui.mostrar_figura(gr.histogramas_amplitud(tablas, "Distribución de la amplitud"), "experimento4_amplitudes", f"{P}_hist")
    with cB:
        conf = np.linspace(0.50, 0.999, 300)
        if E.procedimiento in ("media_t", "dif_medias_t"):
            gl = E.n1 - 1 if E.procedimiento == "media_t" else E.n1 + E.n2 - 2
            cr = np.array([ic.t_critico((1 - c) / 2, gl) for c in conf]); c95 = ic.t_critico(0.025, gl)
            et = f"t con {gl} gl"
        else:
            cr = np.array([ic.z_critico((1 - c) / 2) for c in conf]); c95 = ic.z_critico(0.025)
            et = "z"
        fig = go.Figure(go.Scatter(x=conf * 100, y=cr / c95, mode="lines", line=dict(color=gr.AZUL, width=2.2),
                                   name="Amplitud relativa", hovertemplate="%{x:.1f} %<br>× %{y:.3f}<extra></extra>"))
        for nv in niv_guardados:
            a = 1 - nv / 100
            v = (ic.t_critico(a / 2, gl) if E.procedimiento in ("media_t", "dif_medias_t") else ic.z_critico(a / 2)) / c95
            fig.add_trace(go.Scatter(x=[nv], y=[v], mode="markers+text", text=[f"{nv:g} %: ×{v:.3f}"],
                                     textposition="top left", marker=dict(color=gr.TINTA, size=9), showlegend=False))
        gr._base(fig, f"El precio de la confianza ({et})", 400, x="Nivel de confianza (%)",
                 y="Amplitud relativa al 95 %")
        fig.update_layout(showlegend=False)
        ui.mostrar_figura(fig, "experimento4_precio", f"{P}_precio")
        if E.procedimiento in ("varianza_chi2", "exponencial_chi2", "razon_varianzas_f"):
            ui.nota("Para χ² y F la amplitud depende de dos cuantiles asimétricos; la curva mostrada es la de Z como referencia.")
    st.dataframe(df.style.format({"α": "{:.3f}", "valor crítico": "{:.4f}", "amplitud media": "{:.4f}",
                                  "cobertura empírica": "{:.4f}", "ee Monte Carlo": "{:.4f}", "amplitud relativa": "{:.3f}"}),
                 hide_index=True, use_container_width=True)

with fund:
    z90, z95, z99 = ic.z_critico(.05), ic.z_critico(.025), ic.z_critico(.005)
    st.markdown(rf"""
**Lo único que cambia es el valor crítico.** Para los intervalos de la forma $\hat\theta\pm c_\alpha\,\sigma_{{\hat\theta}}$,
con las mismas muestras el estimador y el error estándar son idénticos, y la amplitud es $A=2c_\alpha\sigma_{{\hat\theta}}$.
Por tanto, la razón de amplitudes entre dos niveles **no depende de los datos**:
$$\frac{{A_{{99\%}}}}{{A_{{95\%}}}}=\frac{{z_{{.005}}}}{{z_{{.025}}}}=\frac{{{z99:.4f}}}{{{z95:.4f}}}={z99 / z95:.4f},\qquad
\frac{{A_{{90\%}}}}{{A_{{95\%}}}}=\frac{{z_{{.05}}}}{{z_{{.025}}}}=\frac{{{z90:.4f}}}{{{z95:.4f}}}={z90 / z95:.4f}.$$

**Por qué crece el valor crítico.** $z_{{\alpha/2}}$ deja un área $\alpha/2$ en cada cola (Figura 8.7). Pedir más confianza
es pedir menos área en las colas, y eso obliga a ir más lejos del centro. Cuando $1-\alpha\to1$, $z_{{\alpha/2}}\to\infty$:
un intervalo con 100 % de confianza tendría que ser toda la recta real, y no serviría para nada.

**El compromiso.** El libro pide intervalos que tengan «una alta probabilidad de incluir a θ» y que sean «estrechos»
(Sección 8.5, p. 406). Con $n$ fijo, las dos metas se oponen. La única manera de ganar en ambas es aumentar $n$.
Para mantener la amplitud del 95 % pero con 99 % de confianza, hace falta multiplicar $n$ por
$(z_{{.005}}/z_{{.025}})^2={(z99 / z95) ** 2:.3f}$ (Sección 8.7).

**Anidamiento y cobertura.** Como los intervalos están anidados, $\{{\theta\in IC_{{90}}\}}\subseteq\{{\theta\in IC_{{95}}\}}\subseteq\{{\theta\in IC_{{99}}\}}$.
Con las mismas muestras, la cobertura empírica es **monótona** en el nivel, no solo en promedio.

**Para t.** El valor crítico depende de $n-1$ (Tabla 5); con $n$ pequeño, el precio de la confianza es mayor que con Z,
porque las colas de la $t$ son más pesadas.
""")
    ui.ficha(E.proc)

with datos:
    nivel_sel = st.selectbox("Nivel", list(tablas.keys()), key=f"{P}_tab")
    st.dataframe(tablas[nivel_sel], use_container_width=True, height=320)
    ui.descargar_tabla(tablas[nivel_sel], f"experimento4_intervalos_{nivel_sel.replace(' %', '')}", P, ui.metadatos(E))
