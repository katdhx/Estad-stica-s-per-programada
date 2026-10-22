"""Gráficos Plotly con la paleta común (α rojo, β azul, potencia verde)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

from . import binomial as bn
from . import pruebaz as pz
from .ui import ALFA, BETA, GRIS, GRIS_CLARO, NAVY, POTENCIA

FUENTE = dict(family="Georgia, 'Times New Roman', serif", color=NAVY, size=13)


def _estilo(fig: go.Figure, alto: int = 420, titulo: str | None = None) -> go.Figure:
    fig.update_layout(template="plotly_white", height=alto, font=FUENTE, margin=dict(l=55, r=20, t=55, b=40),
                      legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="left", x=0),
                      title=dict(text=titulo, font=dict(size=15)) if titulo else None, hovermode="x unified")
    return fig


def _rgba(hexa: str, a: float) -> str:
    h = hexa.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


# ------------------------------------------------------------------------------ Módulo 1

def binomiales(n: int, p0: float, p1: float, c: int, cola: str) -> go.Figure:
    y = np.arange(n + 1)
    rr = bn.en_region(y, c, cola)
    f0 = stats.binom.pmf(y, n, p0)
    f1 = stats.binom.pmf(y, n, p1)
    a = bn.alfa(n, p0, c, cola)
    b = bn.beta(n, p1, c, cola)
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06,
                        subplot_titles=(f"Bajo H₀: p = {p0:.2f}  (α = {a:.4f})",
                                        f"Bajo p₁ = {p1:.2f}  (β = {b:.4f})"))
    fig.add_trace(go.Bar(x=y, y=f0, marker_color=np.where(rr, ALFA, GRIS_CLARO), name="P(Y = y | p₀)",
                         hovertemplate="y = %{x}<br>P = %{y:.5f}<extra></extra>", showlegend=False), 1, 1)
    fig.add_trace(go.Bar(x=y, y=f1, marker_color=np.where(rr, POTENCIA, BETA), name="P(Y = y | p₁)",
                         hovertemplate="y = %{x}<br>P = %{y:.5f}<extra></extra>", showlegend=False), 1, 2)
    # leyenda manual
    for nombre, color in (("Región de rechazo bajo H₀ → α", ALFA), ("No rechazo bajo p₁ → β", BETA),
                          ("Rechazo bajo p₁ → potencia", POTENCIA), ("No rechazo bajo H₀", GRIS_CLARO)):
        fig.add_trace(go.Bar(x=[None], y=[None], marker_color=color, name=nombre), 1, 1)
    borde = c + 0.5 if cola == "inferior" else c - 0.5
    for col in (1, 2):
        fig.add_vline(x=borde, line_dash="dash", line_color=NAVY, line_width=1.5, row=1, col=col)
        fig.update_xaxes(title_text="y (votantes a favor)", dtick=1 if n <= 30 else 5, row=1, col=col)
    fig.update_yaxes(title_text="Probabilidad", row=1, col=1)
    fig.update_layout(bargap=0.12)
    _estilo(fig, 470)
    fig.update_layout(hovermode="closest", margin=dict(t=40, b=40), legend=dict(y=-0.22))
    fig.update_annotations(font_size=13)
    return fig


def curva_beta(n: int, p0: float, p1: float, c: int, cola: str) -> go.Figure:
    ps = np.linspace(0.001, 0.999, 500)
    no_rech = bn.curva_beta(n, c, cola, ps)
    en_ha = ps < p0 if cola == "inferior" else ps > p0
    fig = go.Figure()
    x0, x1 = (0, p0) if cola == "inferior" else (p0, 1)
    fig.add_vrect(x0=x0, x1=x1, fillcolor=_rgba(BETA, 0.07), line_width=0, layer="below",
                  annotation_text="Hₐ compuesta: todos estos p", annotation_position="top left" if cola == "inferior"
                  else "top right", annotation_font_color=BETA)
    fig.add_trace(go.Scatter(x=ps[en_ha], y=no_rech[en_ha], mode="lines", line=dict(color=BETA, width=3),
                             name="β(p) en Hₐ", hovertemplate="p = %{x:.3f}<br>β = %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=ps[en_ha], y=1 - no_rech[en_ha], mode="lines", line=dict(color=POTENCIA, width=2),
                             name="Potencia 1 − β(p)", hovertemplate="p = %{x:.3f}<br>potencia = %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=ps[~en_ha], y=no_rech[~en_ha], mode="lines", line=dict(color=GRIS, width=1.5, dash="dot"),
                             name="P(no rechazar) fuera de Hₐ (no es β)", hoverinfo="skip"))
    b1 = bn.beta(n, p1, c, cola)
    fig.add_trace(go.Scatter(x=[p1], y=[b1], mode="markers+text", marker=dict(size=13, color=BETA, line=dict(color=NAVY, width=2)),
                             text=[f"  β({p1:.2f}) = {b1:.3f}"], textposition="middle right" if cola == "inferior" else "middle left",
                             name="Alternativa específica p₁", hovertemplate="p₁ = %{x:.3f}<br>β = %{y:.4f}<extra></extra>"))
    a = bn.alfa(n, p0, c, cola)
    fig.add_trace(go.Scatter(x=[p0], y=[1 - a], mode="markers", marker=dict(size=11, color=ALFA, symbol="diamond"),
                             name=f"En p₀: P(no rechazar) = 1 − α = {1 - a:.4f}",
                             hovertemplate="p₀ = %{x:.2f}<extra></extra>"))
    fig.add_vline(x=p0, line_dash="dash", line_color=NAVY, line_width=1)
    fig.update_xaxes(title_text="Valor verdadero de p", range=[0, 1])
    fig.update_yaxes(title_text="Probabilidad", range=[-0.02, 1.05])
    _estilo(fig, 420, "β(p): el riesgo de error tipo II para cada valor de la alternativa")
    fig.update_layout(hovermode="closest")
    return fig


# ------------------------------------------------------------------------------ Módulo 2

def normales(cfg: pz.ConfigZ, k: float) -> go.Figure:
    ee = cfg.ee
    lo = min(cfg.mu0, cfg.mu1, k) - 4 * ee
    hi = max(cfg.mu0, cfg.mu1, k) + 4 * ee
    x = np.linspace(lo, hi, 900)
    f0 = stats.norm.pdf(x, cfg.mu0, ee)
    f1 = stats.norm.pdf(x, cfg.mu1, ee)
    rr = x > k if cfg.cola == "superior" else x < k
    r = pz.resumen(cfg, k)
    fig = go.Figure()

    def area(mask, y, color, nombre, op):
        yy = np.where(mask, y, np.nan)
        fig.add_trace(go.Scatter(x=x, y=yy, mode="lines", line=dict(width=0), fill="tozeroy",
                                 fillcolor=_rgba(color, op), name=nombre, hoverinfo="skip", connectgaps=False))

    area(rr, f1, POTENCIA, f"Potencia = {r['potencia']:.4f}", 0.35)
    area(~rr, f1, BETA, f"β = {r['beta']:.4f}", 0.45)
    area(rr, f0, ALFA, f"α = {r['alfa']:.4f}", 0.85)
    fig.add_trace(go.Scatter(x=x, y=f0, mode="lines", line=dict(color=NAVY, width=2.5), name=f"Ȳ bajo H₀ (μ = {cfg.mu0:g})",
                             hovertemplate="ȳ = %{x:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=x, y=f1, mode="lines", line=dict(color=GRIS, width=2.5, dash="dash"),
                             name=f"Ȳ bajo μ₁ = {cfg.mu1:g}", hoverinfo="skip"))
    fig.add_vline(x=k, line_color=NAVY, line_width=2, annotation_text=f"k = {k:.3f}", annotation_position="top")
    ymax = max(f0.max(), f1.max())
    lado = "→ rechazar H₀" if cfg.cola == "superior" else "rechazar H₀ ←"
    fig.add_annotation(x=k + (0.6 if cfg.cola == "superior" else -0.6) * ee, y=ymax * 1.05, text=lado,
                       showarrow=False, font=dict(color=ALFA))
    fig.update_xaxes(title_text="Valor de la media muestral ȳ")
    fig.update_yaxes(title_text="Densidad", range=[0, ymax * 1.15])
    _estilo(fig, 440, "Distribución muestral de Ȳ bajo H₀ y bajo la alternativa específica")
    fig.update_layout(hovermode="closest")
    return fig


def alfa_beta_vs_k(cfg: pz.ConfigZ, k: float) -> go.Figure:
    ee = cfg.ee
    ks = np.linspace(min(cfg.mu0, cfg.mu1) - 3 * ee, max(cfg.mu0, cfg.mu1) + 3 * ee, 400)
    a = pz.alfa_de_frontera(cfg, ks)
    b = pz.beta_de_frontera(cfg, ks)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ks, y=a, name="α(k)", line=dict(color=ALFA, width=3)))
    fig.add_trace(go.Scatter(x=ks, y=b, name="β(k) en μ₁", line=dict(color=BETA, width=3)))
    fig.add_vline(x=k, line_color=NAVY, line_dash="dash", annotation_text="k actual")
    fig.update_xaxes(title_text="Frontera k")
    fig.update_yaxes(title_text="Probabilidad", range=[0, 1])
    return _estilo(fig, 330, "Mover k: un error baja y el otro sube")


def beta_vs_n(cfg: pz.ConfigZ, n_req: int | None) -> go.Figure:
    tope = max(cfg.n, n_req or 0) * 2 + 10
    ns = np.arange(1, int(tope) + 1)
    b = pz.beta_vs_n(cfg, ns)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=b, name="β(μ₁) con α fijo", line=dict(color=BETA, width=3),
                             hovertemplate="n = %{x}<br>β = %{y:.4f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=ns, y=np.full_like(b, cfg.alfa), name=f"α = {cfg.alfa:g} (fijo)",
                             line=dict(color=ALFA, width=2, dash="dash"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[cfg.n], y=[float(pz.beta_vs_n(cfg, [cfg.n])[0])], mode="markers",
                             marker=dict(size=12, color=NAVY), name=f"n actual = {cfg.n}"))
    if n_req:
        fig.add_vline(x=n_req, line_color=POTENCIA, line_dash="dot", annotation_text=f"n requerido = {n_req}")
    fig.update_xaxes(title_text="Tamaño de muestra n")
    fig.update_yaxes(title_text="Probabilidad", range=[0, 1])
    _estilo(fig, 330, "Con más datos se pueden bajar los dos errores a la vez")
    fig.update_layout(hovermode="closest")
    return fig


# ------------------------------------------------------------------------------ Módulo 3

def _reducir(df: pd.DataFrame, max_puntos: int = 2500) -> pd.DataFrame:
    if len(df) <= max_puntos:
        return df
    idx = np.unique(np.geomspace(1, len(df), max_puntos).astype(int) - 1)
    return df.iloc[idx]


def trayectorias(tray1: pd.DataFrame, a_teo: float, tray2: pd.DataFrame, b_teo: float) -> go.Figure:
    fig = go.Figure()
    for tray, teo, color, nombre in ((tray1, a_teo, ALFA, "tipo I"), (tray2, b_teo, BETA, "tipo II")):
        if tray.empty:
            continue
        t = _reducir(tray)
        m = t["m"].to_numpy(dtype=float)
        banda = 1.96 * np.sqrt(teo * (1 - teo) / m)
        fig.add_trace(go.Scatter(x=np.r_[m, m[::-1]], y=np.r_[np.clip(teo + banda, 0, 1), np.clip(teo - banda, 0, 1)[::-1]],
                                 fill="toself", fillcolor=_rgba(color, 0.12), line=dict(width=0), hoverinfo="skip",
                                 name=f"Teórica ± 1.96·EE ({nombre})"))
        fig.add_trace(go.Scatter(x=m, y=t["frecuencia"], mode="lines", line=dict(color=color, width=2),
                                 name=f"Frecuencia empírica de error {nombre}",
                                 hovertemplate="m = %{x}<br>frecuencia = %{y:.4f}<extra></extra>"))
        fig.add_hline(y=teo, line_color=color, line_dash="dash", line_width=1)
    fig.update_xaxes(title_text="Número de experimentos con ese estado verdadero (escala log)", type="log")
    fig.update_yaxes(title_text="Frecuencia acumulada de error", range=[0, 1])
    _estilo(fig, 430, "Las frecuencias se estabilizan alrededor de la probabilidad teórica")
    fig.update_layout(hovermode="closest")
    return fig


def conteo_resultados(df: pd.DataFrame) -> go.Figure:
    orden = ["Decisión correcta", "Error tipo I", "Error tipo II"]
    colores = {"Decisión correcta": NAVY, "Error tipo I": ALFA, "Error tipo II": BETA}
    tabla = df.groupby(["estado", "resultado"]).size().reset_index(name="cuenta")
    fig = go.Figure()
    for res in orden:
        sub = tabla[tabla["resultado"] == res]
        fig.add_trace(go.Bar(x=sub["estado"], y=sub["cuenta"], name=res, marker_color=colores[res],
                             text=sub["cuenta"], textposition="auto"))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text="Experimentos")
    _estilo(fig, 330, "Qué pasó en cada experimento")
    fig.update_layout(hovermode="closest")
    return fig


# ------------------------------------------------------------------------------ datos y signos

def histograma_datos(x: np.ndarray, mu0: float, ybar: float, titulo: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=x, marker_color=_rgba(NAVY, 0.55), marker_line=dict(color=NAVY, width=1),
                               name="Observaciones", nbinsx=min(40, max(8, int(np.sqrt(len(x))) + 2))))
    fig.add_vline(x=mu0, line_color=GRIS, line_dash="dash", annotation_text=f"μ₀ = {mu0:g}")
    fig.add_vline(x=ybar, line_color=ALFA, line_width=2.5, annotation_text=f"ȳ = {ybar:.3f}",
                  annotation_position="top left")
    fig.update_xaxes(title_text="Valor observado")
    fig.update_yaxes(title_text="Frecuencia")
    _estilo(fig, 340, titulo)
    fig.update_layout(hovermode="closest", showlegend=False)
    return fig


def muestra_signos(x: np.ndarray, m0: float) -> go.Figure:
    arriba = x > m0
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x[arriba], y=np.zeros(arriba.sum()), mode="markers", name="signo +",
                             marker=dict(color=POTENCIA, size=12, symbol="triangle-up")))
    fig.add_trace(go.Scatter(x=x[~arriba], y=np.zeros((~arriba).sum()), mode="markers", name="signo −",
                             marker=dict(color=GRIS, size=12, symbol="triangle-down")))
    fig.add_vline(x=m0, line_color=NAVY, line_dash="dash", annotation_text="m₀")
    fig.update_yaxes(visible=False, range=[-1, 1])
    fig.update_xaxes(title_text="Observación")
    _estilo(fig, 200)
    fig.update_layout(hovermode="closest", margin=dict(t=30))
    return fig
