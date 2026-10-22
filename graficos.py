"""Figuras Plotly con la identidad visual del laboratorio.

Codificación del color
----------------------
- Intervalo que CONTIENE al parámetro:     azul   #2a78d6, trazo fino.
- Intervalo que NO lo contiene:            naranja #eb6834, trazo grueso y marcador ×.
  (El color nunca va solo: el grosor y el marcador repiten la información.)
- Curvas teóricas:                          tinta  #1c2733, trazo discontinuo.
- Series de comparación (hasta tres):       azul, naranja, aqua, en ese orden fijo.
Paleta validada para daltonismo con el validador del método de visualización.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

TINTA = "#1c2733"
GRAFITO = "#5a6672"
REGLA = "#e6e9ec"
PAPEL = "#ffffff"
AZUL = "#2a78d6"
NARANJA = "#eb6834"
AQUA = "#1baf7a"
SERIES = (AZUL, NARANJA, AQUA)
FUENTE = "Public Sans, Segoe UI, Helvetica, Arial, sans-serif"
FUENTE_TITULO = "Source Serif 4, Cambria, Georgia, serif"

CONFIG = {
    "displaylogo": False,
    "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "laboratorio_ic"},
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
}


def _base(fig: go.Figure, titulo: str | None = None, alto: int = 420, x: str = "", y: str = "") -> go.Figure:
    fig.update_layout(
        template="none",
        height=alto,
        margin=dict(l=64, r=24, t=56 if titulo else 24, b=110),
        paper_bgcolor=PAPEL,
        plot_bgcolor=PAPEL,
        font=dict(family=FUENTE, size=13, color=TINTA),
        title=dict(text=titulo, x=0, xanchor="left", font=dict(family=FUENTE_TITULO, size=17, color=TINTA))
        if titulo else None,
        legend=dict(orientation="h", yanchor="top", y=-0.24, xanchor="left", x=0,
                    bgcolor="rgba(255,255,255,0)", font=dict(size=12, color=GRAFITO)),
        hoverlabel=dict(bgcolor=PAPEL, bordercolor=GRAFITO, font=dict(family=FUENTE, color=TINTA)),
    )
    eje = dict(showgrid=True, gridcolor=REGLA, zeroline=False, linecolor=GRAFITO, ticks="outside",
               tickcolor=GRAFITO, tickfont=dict(color=GRAFITO), title_font=dict(color=TINTA, size=13))
    fig.update_xaxes(title_text=x, **eje)
    fig.update_yaxes(title_text=y, **eje)
    return fig


# =====================================================================
# Experimento 1: intervalos apilados (análogo a la Figura 8.8 del libro)
# =====================================================================
def intervalos_apilados(tabla: pd.DataFrame, theta: float, etiqueta_parametro: str,
                        resaltar: int | None = None, titulo: str | None = None) -> go.Figure:
    t = tabla
    fin = np.isfinite(t["L"]) & np.isfinite(t["U"])
    finitos = np.concatenate([t["L"][np.isfinite(t["L"])], t["U"][np.isfinite(t["U"])], [theta]])
    lo, hi = float(np.min(finitos)), float(np.max(finitos))
    margen = 0.08 * (hi - lo if hi > lo else 1.0)
    xmin, xmax = lo - margen, hi + margen
    L = t["L"].clip(lower=xmin).to_numpy()
    U = t["U"].clip(upper=xmax).to_numpy()
    y = t["replica"].to_numpy()

    fig = go.Figure()
    for cubre, color, ancho, nombre in ((True, AZUL, 2, "Contiene el parámetro"),
                                        (False, NARANJA, 3.5, "No contiene el parámetro")):
        m = (t["cubre"] == cubre).to_numpy()
        if not m.any():
            continue
        xs = np.column_stack([L[m], U[m], np.full(m.sum(), np.nan)]).ravel()
        ys = np.column_stack([y[m], y[m], np.full(m.sum(), np.nan)]).ravel()
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=ancho),
                                   name=nombre, hoverinfo="skip", legendgroup=nombre))
        fig.add_trace(go.Scatter(
            x=t["estimador"][m], y=y[m], mode="markers", legendgroup=nombre, showlegend=False,
            marker=dict(color=color, size=7 if cubre else 9, symbol="circle" if cubre else "x",
                        line=dict(color=PAPEL, width=1) if cubre else None),
            customdata=np.column_stack([t["L"][m], t["U"][m], t["amplitud"][m]]),
            hovertemplate=("Muestra %{y}<br>Estimación %{x:.4f}<br>L = %{customdata[0]:.4f}"
                           "<br>U = %{customdata[1]:.4f}<br>Amplitud %{customdata[2]:.4f}<extra></extra>"),
        ))
    if resaltar is not None and 1 <= resaltar <= len(t):
        f = t.iloc[resaltar - 1]
        fig.add_hrect(y0=resaltar - 0.5, y1=resaltar + 0.5, fillcolor="rgba(28,39,51,0.08)", line_width=0)
        fig.add_annotation(x=float(np.clip(f["U"], xmin, xmax)), y=resaltar, text=f"  muestra {resaltar}",
                           showarrow=False, xanchor="left", font=dict(color=TINTA, size=12))
    fig.add_vline(x=theta, line=dict(color=TINTA, width=1.5, dash="dash"))
    fig.add_annotation(x=theta, y=1.0, yref="paper", yanchor="bottom", text=f"{etiqueta_parametro} = {theta:.4g}",
                       showarrow=False, font=dict(color=TINTA, size=12))
    alto = int(min(900, max(360, 14 * len(t) + 120)))
    _base(fig, titulo, alto, x="Valor del parámetro", y="Muestra")
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(range=[xmin, xmax])
    if not fin.all():
        fig.add_annotation(x=0, y=-0.3, xref="paper", yref="paper", showarrow=False, xanchor="left",
                           text="Intervalos unilaterales: el extremo infinito se dibuja recortado en el borde.",
                           font=dict(color=GRAFITO, size=11))
    return fig


def cobertura_acumulada(cubre: np.ndarray, nominal: float, titulo: str | None = None) -> go.Figure:
    """Proporción acumulada de intervalos que cubren, con la banda de fluctuación Monte Carlo."""
    c = np.asarray(cubre, dtype=float)
    k = np.arange(1, c.size + 1)
    acum = np.cumsum(c) / k
    paso = max(1, c.size // 2000)
    k_, a_ = k[::paso], acum[::paso]
    banda = 1.96 * np.sqrt(nominal * (1 - nominal) / k_)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.r_[k_, k_[::-1]], y=np.r_[nominal + banda, (nominal - banda)[::-1]],
                             mode="lines", fill="toself", fillcolor="rgba(28,39,51,0.08)", line=dict(width=0),
                             name="Banda 1 − α ± 1.96·√(c(1−c)/k)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=k_, y=a_, mode="lines", line=dict(color=AZUL, width=2),
                             name="Cobertura acumulada", hovertemplate="k = %{x}<br>ĉ = %{y:.4f}<extra></extra>"))
    fig.add_hline(y=nominal, line=dict(color=TINTA, width=1.2, dash="dot"))
    _base(fig, titulo, 360, x="Número de intervalos construidos k", y="Proporción que contiene el parámetro")
    fig.update_xaxes(type="log")
    lo = max(0.0, min(float(a_.min()), nominal - 0.1) - 0.02)
    fig.update_yaxes(range=[lo, 1.0])
    return fig


# =====================================================================
# Experimentos 2, 3 y 6: curvas en función de n
# =====================================================================
def curva_vs_n(df: pd.DataFrame, columna: str, etiquetas: dict[str, str], titulo: str | None = None,
               y: str = "", teorico: dict[str, tuple[np.ndarray, np.ndarray]] | None = None,
               nominal: float | None = None, columna_error: str | None = None, logy: bool = False,
               B: int | None = None) -> go.Figure:
    fig = go.Figure()
    if nominal is not None and B:
        ns = np.sort(df["n"].unique())
        b = 1.96 * np.sqrt(nominal * (1 - nominal) / B)
        fig.add_trace(go.Scatter(x=np.r_[ns, ns[::-1]], y=np.r_[np.full(ns.size, nominal + b), np.full(ns.size, nominal - b)],
                                 mode="lines", fill="toself", fillcolor="rgba(28,39,51,0.07)", line=dict(width=0),
                                 name=f"Fluctuación Monte Carlo esperada (B = {B:,})".replace(",", " "),
                                 hoverinfo="skip"))
    for i, (clave, sub) in enumerate(df.groupby("procedimiento", sort=False)):
        color = SERIES[i % len(SERIES)]
        err = None
        if columna_error and columna_error in sub:
            err = dict(type="data", array=1.96 * sub[columna_error], color=color, thickness=1.2, width=4)
        simbolo = ("circle", "diamond", "square", "triangle-up", "x", "star")[i % 6]
        trazo = "solid" if i < 3 else "dot"
        fig.add_trace(go.Scatter(
            x=sub["n"], y=sub[columna], mode="lines+markers", name=etiquetas.get(clave, clave),
            line=dict(color=color, width=2, dash=trazo),
            marker=dict(size=9, color=color, symbol=simbolo, line=dict(color=PAPEL, width=1.5)),
            error_y=err, hovertemplate="n = %{x}<br>%{y:.4f}<extra>" + etiquetas.get(clave, clave) + "</extra>",
        ))
        if teorico and clave in teorico:
            xs, ys = teorico[clave]
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=TINTA, width=1.5, dash="dash"),
                                     name=f"Teórico: {etiquetas.get(clave, clave)}",
                                     hovertemplate="n = %{x}<br>teórico %{y:.4f}<extra></extra>"))
    if nominal is not None:
        fig.add_hline(y=nominal, line=dict(color=TINTA, width=1.2, dash="dot"),
                      annotation_text=f"nominal {nominal:.0%}", annotation_position="bottom right",
                      annotation_font=dict(color=GRAFITO, size=11))
    _base(fig, titulo, 420, x="Tamaño muestral n (escala logarítmica)", y=y)
    fig.update_xaxes(type="log")
    if logy:
        fig.update_yaxes(type="log")
    return fig


def trayectoria(df: pd.DataFrame, theta: float, etiqueta: str, titulo: str | None = None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.r_[df["n"], df["n"][::-1]], y=np.r_[df["U"], df["L"][::-1]],
                             mode="lines", fill="toself", fillcolor="rgba(42,120,214,0.15)", line=dict(width=0),
                             name="Intervalo con las primeras n observaciones", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=df["n"], y=df["estimador"], mode="lines", line=dict(color=AZUL, width=2),
                             name="Estimación puntual",
                             customdata=np.column_stack([df["L"], df["U"]]),
                             hovertemplate="n = %{x}<br>estimación %{y:.4f}<br>[%{customdata[0]:.4f}, %{customdata[1]:.4f}]<extra></extra>"))
    fig.add_hline(y=theta, line=dict(color=TINTA, width=1.5, dash="dash"),
                  annotation_text=f"{etiqueta} = {theta:.4g}", annotation_position="top right",
                  annotation_font=dict(color=TINTA, size=12))
    _base(fig, titulo, 420, x="Número de observaciones usadas n (escala logarítmica)", y="Valor")
    fig.update_xaxes(type="log")
    return fig


# =====================================================================
# Experimento 4: niveles de confianza sobre las mismas muestras
# =====================================================================
def niveles_anidados(tablas: dict[str, pd.DataFrame], theta: float, etiqueta: str, k: int = 30,
                     titulo: str | None = None) -> go.Figure:
    fig = go.Figure()
    niveles = list(tablas.keys())
    desplaz = np.linspace(-0.25, 0.25, len(niveles))
    for i, nivel in enumerate(niveles):
        t = tablas[nivel].head(k)
        color = SERIES[i % len(SERIES)]
        y = t["replica"].to_numpy() + desplaz[i]
        xs = np.column_stack([t["L"], t["U"], np.full(len(t), np.nan)]).ravel()
        ys = np.column_stack([y, y, np.full(len(t), np.nan)]).ravel()
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=2.5), name=nivel,
                                 hoverinfo="skip", legendgroup=nivel))
        fig.add_trace(go.Scatter(
            x=(t["L"] + t["U"]) / 2, y=y, mode="markers", marker=dict(size=4, color=color), showlegend=False,
            legendgroup=nivel, customdata=np.column_stack([t["L"], t["U"], t["cubre"].astype(int)]),
            hovertemplate=nivel + "<br>[%{customdata[0]:.4f}, %{customdata[1]:.4f}]<br>¿cubre? %{customdata[2]}<extra></extra>"))
        malos = t[~t["cubre"]]
        if len(malos):
            fig.add_trace(go.Scatter(x=malos["U"], y=malos["replica"] + desplaz[i], mode="markers",
                                     marker=dict(symbol="x", size=9, color=color), showlegend=False,
                                     hoverinfo="skip", legendgroup=nivel))
    fig.add_vline(x=theta, line=dict(color=TINTA, width=1.5, dash="dash"))
    fig.add_annotation(x=theta, y=1.0, yref="paper", yanchor="bottom", text=f"{etiqueta} = {theta:.4g}",
                       showarrow=False, font=dict(color=TINTA, size=12))
    _base(fig, titulo, int(max(380, 18 * k + 120)), x="Valor del parámetro", y="Muestra")
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return fig


def histogramas_amplitud(tablas: dict[str, pd.DataFrame], titulo: str | None = None) -> go.Figure:
    fig = go.Figure()
    for i, (nivel, t) in enumerate(tablas.items()):
        a = t["amplitud"].to_numpy()
        a = a[np.isfinite(a)]
        fig.add_trace(go.Histogram(x=a, name=nivel, marker=dict(color=SERIES[i % 3], line=dict(color=PAPEL, width=1)),
                                   opacity=0.75, nbinsx=50, histnorm="probability density"))
    _base(fig, titulo, 360, x="Amplitud del intervalo", y="Densidad")
    fig.update_layout(barmode="overlay")
    return fig


# =====================================================================
# Experimento 5: histograma frente a densidades teóricas
# =====================================================================
def histograma_densidades(valores: np.ndarray, curvas: list[tuple[str, callable, str]], titulo: str | None = None,
                          x: str = "", rango: tuple[float, float] | None = None, discreto: bool = False,
                          sombrear: tuple[float, float] | None = None, bins: int = 60) -> go.Figure:
    v = np.asarray(valores, dtype=float)
    v = v[np.isfinite(v)]
    if rango is None:
        lo, hi = np.quantile(v, [0.001, 0.999]) if v.size > 50 else (v.min(), v.max())
        pad = 0.05 * (hi - lo if hi > lo else 1)
        rango = (lo - pad, hi + pad)
    fig = go.Figure()
    if discreto:
        vals, cuentas = np.unique(v, return_counts=True)
        fig.add_trace(go.Bar(x=vals, y=cuentas / v.size, name="Frecuencia relativa simulada",
                             marker=dict(color=AZUL, line=dict(color=PAPEL, width=2)), opacity=0.8))
    else:
        fig.add_trace(go.Histogram(
            x=v, histnorm="probability density", name="Distribución empírica (simulación)",
            xbins=dict(start=rango[0], end=rango[1], size=(rango[1] - rango[0]) / bins),
            marker=dict(color="rgba(42,120,214,0.45)", line=dict(color=PAPEL, width=1)),
        ))
    xs = np.linspace(rango[0], rango[1], 600)
    estilos = {"solida": "solid", "discontinua": "dash", "punteada": "dot"}
    colores = [TINTA, NARANJA, AQUA]
    for i, (nombre, f, estilo) in enumerate(curvas):
        if f is None:
            continue
        with np.errstate(all="ignore"):
            ys = f(xs)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=nombre,
                                 line=dict(color=colores[i % 3], width=2.2, dash=estilos.get(estilo, "solid"))))
    if sombrear is not None:
        a, b = sombrear
        fig.add_vrect(x0=max(a, rango[0]), x1=min(b, rango[1]), fillcolor="rgba(28,39,51,0.06)", line_width=0)
        for lim in (a, b):
            if rango[0] <= lim <= rango[1]:
                fig.add_vline(x=lim, line=dict(color=GRAFITO, width=1, dash="dot"))
    _base(fig, titulo, 400, x=x, y="Densidad" if not discreto else "Probabilidad")
    fig.update_xaxes(range=list(rango))
    return fig


def dispersion(x: np.ndarray, y: np.ndarray, titulo: str | None = None, xl: str = "", yl: str = "",
               max_puntos: int = 3000) -> go.Figure:
    k = min(len(x), max_puntos)
    fig = go.Figure(go.Scattergl(x=x[:k], y=y[:k], mode="markers",
                                 marker=dict(size=5, color="rgba(42,120,214,0.45)"),
                                 hovertemplate=f"{xl} = %{{x:.4f}}<br>{yl} = %{{y:.4f}}<extra></extra>",
                                 name="Réplicas"))
    _base(fig, titulo, 380, x=xl, y=yl)
    return fig


def barras_comparacion(etiquetas: list[str], valores: list[float], referencia: float | None = None,
                       titulo: str | None = None, y: str = "", errores: list[float] | None = None,
                       ref_texto: str = "") -> go.Figure:
    fig = go.Figure(go.Bar(
        x=etiquetas, y=valores, marker=dict(color=AZUL, line=dict(color=PAPEL, width=2)),
        error_y=dict(type="data", array=errores, color=TINTA, thickness=1.2) if errores else None,
        text=[f"{v:.4f}" for v in valores], textposition="inside", insidetextanchor="start",
        textfont=dict(color=PAPEL, size=13), cliponaxis=False,
        hovertemplate="%{x}<br>%{y:.5f}<extra></extra>",
    ))
    if referencia is not None:
        fig.add_hline(y=referencia, line=dict(color=TINTA, width=1.4, dash="dash"),
                      annotation_text=ref_texto, annotation_position="top left",
                      annotation_font=dict(color=TINTA, size=12))
    _base(fig, titulo, 380, y=y)
    fig.update_layout(showlegend=False, bargap=0.45)
    return fig


def curva_p(ps: np.ndarray, exacta: np.ndarray, nominal: float, mc: pd.DataFrame | None = None,
            titulo: str | None = None, zona_regla: tuple[float, float] | None = None) -> go.Figure:
    fig = go.Figure()
    if zona_regla is not None:
        fig.add_vrect(x0=zona_regla[0], x1=zona_regla[1], fillcolor="rgba(27,175,122,0.08)", line_width=0,
                      annotation_text="Cumple la regla p ± 3√(pq/n) ∈ (0, 1)", annotation_position="top left",
                      annotation_font=dict(color=GRAFITO, size=11))
    fig.add_trace(go.Scatter(x=ps, y=exacta, mode="lines", line=dict(color=AZUL, width=1.8),
                             name="Cobertura exacta (suma binomial)",
                             hovertemplate="p = %{x:.3f}<br>cobertura %{y:.4f}<extra></extra>"))
    if mc is not None and len(mc):
        fig.add_trace(go.Scatter(x=mc["p"], y=mc["cobertura"], mode="markers", name="Cobertura Monte Carlo",
                                 marker=dict(color=NARANJA, size=9, symbol="diamond", line=dict(color=PAPEL, width=1)),
                                 error_y=dict(type="data", array=1.96 * mc["ee"], color=NARANJA, thickness=1.2)))
    fig.add_hline(y=nominal, line=dict(color=TINTA, width=1.2, dash="dot"))
    _base(fig, titulo, 420, x="Proporción verdadera p", y="Cobertura")
    return fig
