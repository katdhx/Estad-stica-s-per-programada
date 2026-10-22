"""Figuras Plotly del Laboratorio F.

Codificación fija del color (paleta validada para daltonismo):
* Simulación (lo empírico): azul  #2a78d6.
* Teoría (densidades del libro): tinta #18343a, trazo continuo o discontinuo.
* Colas fuera del intervalo central de la F y lo que «se sale» de la referencia: naranja #eb6834.
* Tercera serie de comparación: aqua #1baf7a.
Nunca se usa el color solo: las curvas llevan nombre en la leyenda o en una etiqueta.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats

TINTA = "#18343a"
GRAFITO = "#55666a"
REGLA = "#e3e9ea"
PAPEL = "#ffffff"
AZUL = "#2a78d6"
NARANJA = "#eb6834"
AQUA = "#1baf7a"
SERIES = (AZUL, NARANJA, AQUA)
FUENTE = "IBM Plex Sans, Segoe UI, Helvetica, Arial, sans-serif"
FUENTE_TITULO = "IBM Plex Serif, Cambria, Georgia, serif"

CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
          "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "laboratorio_f"}}


def base(fig: go.Figure, titulo: str | None = None, alto: int = 420, x: str = "", y: str = "") -> go.Figure:
    fig.update_layout(
        template="none", height=alto, paper_bgcolor=PAPEL, plot_bgcolor=PAPEL,
        margin=dict(l=64, r=24, t=56 if titulo else 24, b=110),
        font=dict(family=FUENTE, size=13, color=TINTA),
        title=dict(text=titulo, x=0, xanchor="left", font=dict(family=FUENTE_TITULO, size=17, color=TINTA)) if titulo else None,
        legend=dict(orientation="h", yanchor="top", y=-72 / max(alto - (56 if titulo else 24) - 110, 120), xanchor="left", x=0, font=dict(size=12, color=GRAFITO),
                    bgcolor="rgba(255,255,255,0)"),
        hoverlabel=dict(bgcolor=PAPEL, bordercolor=GRAFITO, font=dict(family=FUENTE, color=TINTA)),
    )
    eje = dict(showgrid=True, gridcolor=REGLA, zeroline=False, linecolor=GRAFITO, ticks="outside", tickcolor=GRAFITO,
               tickfont=dict(color=GRAFITO), title_font=dict(color=TINTA, size=13))
    fig.update_xaxes(title_text=x, **eje)
    fig.update_yaxes(title_text=y, **eje)
    return fig


def _rango(v: np.ndarray, q: float = 0.995) -> tuple[float, float]:
    v = v[np.isfinite(v)]
    return 0.0, float(np.quantile(v, q)) * 1.05


def poblaciones(formas: list[tuple[str, callable]], titulo: str | None = None, alto: int = 300) -> go.Figure:
    """Densidades de las formas estandarizadas (media 0, varianza 1) frente a la normal."""
    xs = np.linspace(-4, 6, 800)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=stats.norm.pdf(xs), mode="lines", name="Normal estándar (referencia)",
                             line=dict(color=TINTA, width=1.6, dash="dot")))
    for i, (nombre, f) in enumerate(formas):
        with np.errstate(all="ignore"):
            ys = np.nan_to_num(f(xs), nan=0.0, posinf=0.0)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=nombre, line=dict(color=SERIES[i % 3], width=2.4),
                                 fill="tozeroy", fillcolor=["rgba(42,120,214,0.10)", "rgba(235,104,52,0.10)",
                                                            "rgba(27,175,122,0.10)"][i % 3]))
    base(fig, titulo, alto, x="Valor estandarizado (media 0, varianza 1)", y="Densidad")
    fig.update_yaxes(rangemode="tozero")
    fig.update_layout(margin=dict(b=130))
    return fig


def histograma_f(valores: np.ndarray, gl1: int, gl2: int, titulo: str | None = None,
                 region: tuple[float, float] | None = None, exacta: bool = True,
                 x: str = "Valor del estadístico", alto: int = 440, bins: int = 90,
                 etiqueta_teo: str | None = None, etiqueta_region: str = "Colas fuera del intervalo central de la F") -> go.Figure:
    v = np.asarray(valores, dtype=float)
    v = v[np.isfinite(v)]
    lo, hi = _rango(v, 0.99)
    # Se muestra hasta el percentil 99 simulado, sin pasar de 2.5 veces el cuantil .995 de la F:
    # con colas muy pesadas, unos pocos valores extremos aplastarían el resto del gráfico.
    hi = min(max(hi, float(stats.f.ppf(0.99, gl1, gl2))), 2.5 * float(stats.f.ppf(0.995, gl1, gl2)))
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=v, histnorm="probability density", name="Simulación (distribución empírica)",
        xbins=dict(start=0, end=hi, size=hi / bins),
        marker=dict(color="rgba(42,120,214,0.45)", line=dict(color=PAPEL, width=0.6)),
        hovertemplate="%{x}<br>densidad %{y:.3f}<extra></extra>",
    ))
    xs = np.linspace(1e-6, hi, 800)
    nombre = etiqueta_teo or f"F({gl1}, {gl2}) del libro: " + ("referencia exacta" if exacta else "ya NO es la distribución correcta")
    fig.add_trace(go.Scatter(x=xs, y=stats.f.pdf(xs, gl1, gl2), mode="lines", name=nombre,
                             line=dict(color=TINTA, width=2.6, dash="solid" if exacta else "dash")))
    if region is not None:
        a, b = region
        if a > 0:
            xa = np.linspace(1e-6, min(a, hi), 200)
            fig.add_trace(go.Scatter(x=np.r_[xa, xa[::-1]], y=np.r_[stats.f.pdf(xa, gl1, gl2), np.zeros(xa.size)],
                                     fill="toself", fillcolor="rgba(235,104,52,0.35)", line=dict(width=0),
                                     name=etiqueta_region, hoverinfo="skip", mode="lines"))
            fig.add_vline(x=a, line=dict(color=NARANJA, width=1.6, dash="dot"))
        if np.isfinite(b) and b < hi:
            xb = np.linspace(b, hi, 200)
            fig.add_trace(go.Scatter(x=np.r_[xb, xb[::-1]], y=np.r_[stats.f.pdf(xb, gl1, gl2), np.zeros(xb.size)],
                                     fill="toself", fillcolor="rgba(235,104,52,0.35)", line=dict(width=0),
                                     name=etiqueta_region, hoverinfo="skip", mode="lines",
                                     showlegend=a <= 0))
            fig.add_vline(x=b, line=dict(color=NARANJA, width=1.6, dash="dot"))
    base(fig, titulo, alto, x=x, y="Densidad")
    fig.update_xaxes(range=[0, hi])
    return fig


def histograma_chi2(valores: np.ndarray, gl: int, titulo: str | None = None, exacta: bool = True,
                    alto: int = 360, etiqueta_x: str = "W") -> go.Figure:
    v = np.asarray(valores, dtype=float)
    hi = max(float(np.quantile(v, 0.995)), float(stats.chi2.ppf(0.995, gl))) * 1.03
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=v, histnorm="probability density", name="Simulación",
                               xbins=dict(start=0, end=hi, size=hi / 80),
                               marker=dict(color="rgba(42,120,214,0.45)", line=dict(color=PAPEL, width=0.6))))
    xs = np.linspace(1e-6, hi, 600)
    fig.add_trace(go.Scatter(x=xs, y=stats.chi2.pdf(xs, gl), mode="lines",
                             name=f"χ²({gl}) del Teorema 7.3" + ("" if exacta else ": no aplica"),
                             line=dict(color=TINTA, width=2.4, dash="solid" if exacta else "dash")))
    base(fig, titulo, alto, x=etiqueta_x, y="Densidad")
    fig.update_xaxes(range=[0, hi])
    return fig


def colas(tabla: pd.DataFrame, titulo: str | None = None) -> go.Figure:
    """Probabilidad de cola empírica frente a la nominal (barras emparejadas)."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=tabla["cola"], y=tabla["nominal"], name="Lo que promete la F",
                         marker=dict(color="rgba(24,52,58,0.18)", line=dict(color=TINTA, width=1.2)),
                         hovertemplate="%{x}<br>nominal %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Bar(x=tabla["cola"], y=tabla["empirica"], name="Lo que ocurrió en la simulación",
                         marker=dict(color=AZUL, line=dict(color=PAPEL, width=1.5)),
                         error_y=dict(type="data", array=1.96 * tabla["ee"], color=TINTA, thickness=1.2),
                         hovertemplate="%{x}<br>simulada %{y:.4f}<extra></extra>"))
    base(fig, titulo, 400, y="Probabilidad")
    fig.update_layout(barmode="group", bargap=0.35, margin=dict(b=150), legend=dict(y=-0.45))
    fig.update_xaxes(tickangle=-30)
    return fig


def cobertura_vs_n(series: list[tuple[str, pd.DataFrame]], confianza: float, titulo: str | None = None,
                   limites: list[tuple[str, float]] | None = None, B: int | None = None) -> go.Figure:
    fig = go.Figure()
    todos = np.unique(np.concatenate([df["n1"].to_numpy() for _, df in series]))
    if B:
        b = 1.96 * np.sqrt(confianza * (1 - confianza) / B)
        fig.add_trace(go.Scatter(x=np.r_[todos, todos[::-1]], y=np.r_[np.full(todos.size, confianza + b),
                                                                      np.full(todos.size, confianza - b)],
                                 fill="toself", fillcolor="rgba(24,52,58,0.07)", line=dict(width=0), mode="lines",
                                 name="Zona esperable si la F fuera exacta", hoverinfo="skip"))
    for i, (nombre, df) in enumerate(series):
        color = SERIES[i % 3]
        fig.add_trace(go.Scatter(x=df["n1"], y=df["cobertura"], mode="lines+markers", name=nombre,
                                 line=dict(color=color, width=2.4, dash="solid" if i < 3 else "dot"),
                                 marker=dict(size=9, color=color, symbol=("circle", "diamond", "square", "triangle-up")[i % 4],
                                             line=dict(color=PAPEL, width=1.5)),
                                 error_y=dict(type="data", array=1.96 * df["ee"], color=color, thickness=1.1),
                                 hovertemplate="n₁ = %{x}<br>cobertura %{y:.4f}<extra>" + nombre + "</extra>"))
    for i, (nombre, lim) in enumerate(limites or []):
        fig.add_hline(y=lim, line=dict(color=SERIES[i % 3], width=1.2, dash="dash"),
                      annotation_text=f"límite n → ∞ ({nombre}): {lim:.3f}", annotation_position="bottom left",
                      annotation_font=dict(color=SERIES[i % 3], size=11))
    fig.add_hline(y=confianza, line=dict(color=TINTA, width=1.4, dash="dot"),
                  annotation_text=f"prometido: {confianza:.0%}", annotation_position="top right",
                  annotation_font=dict(color=TINTA, size=12))
    base(fig, titulo, 450, x="Tamaño de la muestra 1, n₁ (escala logarítmica)", y="Cobertura real del intervalo")
    fig.update_xaxes(type="log")
    return fig


FAMILIAS = {"normal": (TINTA, "star", "Normal"), "colas livianas": (AQUA, "square", "Colas livianas"),
            "colas pesadas": (NARANJA, "diamond", "Colas pesadas (simétricas)"),
            "asimétrica": (AZUL, "circle", "Asimétricas")}


def mapa_robustez(df: pd.DataFrame, confianza: float, curva: tuple[np.ndarray, np.ndarray], n: int,
                  titulo: str | None = None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curva[0], y=curva[1], mode="lines", name="Curva teórica para n grande (complementaria)",
                             line=dict(color=GRAFITO, width=1.8, dash="dash"), hoverinfo="skip"))
    for fam, (color, simbolo, nombre) in FAMILIAS.items():
        sub = df[df["familia"] == fam]
        if not len(sub):
            continue
        fig.add_trace(go.Scatter(
            x=sub["curtosis"], y=sub["cobertura"], mode="markers+text", name=nombre, customdata=sub["forma"],
            # Solo se rotulan los puntos que no se amontonan; el resto se ve al pasar el cursor.
            text=[f if (k < -0.5 or k > 3 or f == "Normal") else "" for f, k in zip(sub["forma"], sub["curtosis"])],
            textposition="top right", textfont=dict(size=11, color=GRAFITO),
            marker=dict(size=13, color=color, symbol=simbolo, line=dict(color=PAPEL, width=1.5)),
            error_y=dict(type="data", array=1.96 * sub["ee"], color=color, thickness=1),
            hovertemplate="%{customdata}<br>κ = %{x:.2f}<br>cobertura %{y:.4f}<extra></extra>"))
    fig.add_hline(y=confianza, line=dict(color=TINTA, width=1.2, dash="dot"),
                  annotation_text=f"prometido: {confianza:.0%}", annotation_position="top right")
    base(fig, titulo, 540, x="Curtosis en exceso κ (qué tan pesadas son las colas)",
         y=f"Cobertura real del IC del {confianza:.0%} (n₁ = n₂ = {n})")
    return fig


def mapa_calor(df: pd.DataFrame, confianza: float, titulo: str | None = None) -> go.Figure:
    filas = list(dict.fromkeys(df["pob1"]))
    cols = list(dict.fromkeys(df["pob2"]))
    z = df.pivot(index="pob1", columns="pob2", values="cobertura").loc[filas, cols].to_numpy()
    texto = [[f"{v:.3f}" for v in fila] for fila in z]
    escala = [[0.0, "#c4501f"], [0.5, "#f3e2d8"], [0.85, "#f4f6f6"], [1.0, "#1d5c63"]]
    lo = float(min(np.nanmin(z), confianza - 0.15))
    fig = go.Figure(go.Heatmap(
        z=z, x=cols, y=filas, text=texto, texttemplate="%{text}", textfont=dict(size=12),
        colorscale=escala, zmin=lo, zmax=1.0, xgap=3, ygap=3,
        colorbar=dict(title=dict(text="Cobertura", side="right"), tickformat=".2f"),
        hovertemplate="Población 1: %{y}<br>Población 2: %{x}<br>cobertura %{z:.4f}<extra></extra>"))
    base(fig, titulo, 560, x="Forma de la población 2", y="Forma de la población 1")
    fig.update_xaxes(showgrid=False, side="bottom")
    fig.update_yaxes(showgrid=False, autorange="reversed")
    fig.update_layout(margin=dict(l=170, b=120))
    return fig


def intervalos(L: np.ndarray, U: np.ndarray, verdadero: float, titulo: str | None = None) -> go.Figure:
    """Intervalos apilados para σ2²/σ1² (en escala logarítmica, porque es una razón)."""
    k = len(L)
    y = np.arange(1, k + 1)
    cubre = (L <= verdadero) & (verdadero <= U)
    fig = go.Figure()
    for ok, color, ancho, nombre in ((True, AZUL, 2, "Contiene σ₂²/σ₁²"), (False, NARANJA, 3.5, "No lo contiene")):
        m = cubre == ok
        if not m.any():
            continue
        xs = np.column_stack([L[m], U[m], np.full(m.sum(), np.nan)]).ravel()
        ys = np.column_stack([y[m], y[m], np.full(m.sum(), np.nan)]).ravel()
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=ancho), name=nombre,
                                 hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=np.sqrt(L[m] * U[m]), y=y[m], mode="markers", showlegend=False,
                                 marker=dict(size=6 if ok else 9, color=color, symbol="circle" if ok else "x"),
                                 customdata=np.column_stack([L[m], U[m]]),
                                 hovertemplate="Réplica %{y}<br>[%{customdata[0]:.3f}, %{customdata[1]:.3f}]<extra></extra>"))
    # En eje logarítmico, las anotaciones de add_vline se ubican en log10(x) y estiran el eje: se dibuja como traza.
    fig.add_trace(go.Scatter(x=[verdadero, verdadero], y=[0.3, k + 0.7], mode="lines", name=f"σ₂²/σ₁² = {verdadero:g}",
                             line=dict(color=TINTA, width=1.6, dash="dash"), hoverinfo="skip"))
    base(fig, titulo, int(min(900, max(380, 12 * k + 140))), x="σ₂²/σ₁² (escala logarítmica)", y="Réplica")
    lo = float(np.log10(min(np.min(L), verdadero))) - 0.1
    hi = float(np.log10(max(np.max(U), verdadero))) + 0.1
    fig.update_xaxes(type="log", range=[lo, hi])
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return fig


def muestras_par(y1: np.ndarray, y2: np.ndarray, titulo: str | None = None) -> go.Figure:
    fig = go.Figure()
    for i, (y, nombre) in enumerate(((y1, "Muestra 1"), (y2, "Muestra 2"))):
        jitter = np.random.default_rng(i).uniform(-0.18, 0.18, y.size)
        fig.add_trace(go.Scatter(x=y, y=np.full(y.size, i) + jitter, mode="markers", name=nombre,
                                 marker=dict(size=8, color=SERIES[i], opacity=0.75, line=dict(color=PAPEL, width=0.8)),
                                 hovertemplate="%{x:.3f}<extra>" + nombre + "</extra>"))
        m, s = y.mean(), y.std(ddof=1)
        fig.add_shape(type="line", x0=m - s, x1=m + s, y0=i + 0.32, y1=i + 0.32, line=dict(color=SERIES[i], width=4))
        fig.add_annotation(x=m, y=i + 0.45, text=f"ȳ ± s = {m:.2f} ± {s:.2f}", showarrow=False,
                           font=dict(size=11, color=TINTA))
    base(fig, titulo, 280, x="Valor observado", y="")
    fig.update_yaxes(tickvals=[0, 1], ticktext=["Muestra 1", "Muestra 2"], range=[-0.5, 1.75], showgrid=False)
    fig.update_layout(showlegend=False, margin=dict(b=50))
    return fig
