"""Componentes de interfaz compartidos (Streamlit)."""

from __future__ import annotations

import io
from collections import OrderedDict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from . import graficos as gr
from . import motor
from .poblaciones import FORMAS, Forma, Poblacion, forma

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@500;600&display=swap');
:root { --tinta:#18343a; --grafito:#55666a; --regla:#e3e9ea; --petroleo:#1d5c63; --naranja:#c4501f; --suave:#f2f6f6; }
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp td, .stApp th {
  font-family: 'IBM Plex Sans', 'Segoe UI', Helvetica, Arial, sans-serif; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stHeading"] h1, [data-testid="stHeading"] h2, [data-testid="stHeading"] h3 {
  font-family: 'IBM Plex Serif', Cambria, Georgia, 'DejaVu Serif', serif !important; color: var(--tinta); font-weight: 600 !important; }
.stApp h1 { font-size: 2.1rem !important; line-height: 1.18 !important; }
.stApp h2 { font-size: 1.42rem !important; margin-top: 1.5rem !important; }
.stApp h3 { font-size: 1.12rem !important; }
.block-container { max-width: 1200px; padding-top: 2rem; }
p, li { line-height: 1.6; }
.f-pregunta { font-size: 1.1rem; color: var(--grafito); max-width: 48rem; margin: 0 0 .7rem 0; line-height: 1.55; }
.f-ref { font-size: .86rem; color: var(--grafito); border-left: 3px solid var(--petroleo); padding: .1rem 0 .1rem .7rem; margin: .2rem 0 1.2rem 0; }
.f-nota { font-size: .88rem; color: var(--grafito); }
.f-costo { font-size: .84rem; color: var(--grafito); line-height: 1.5; }
.f-veredicto { border-radius: 8px; padding: .8rem 1rem; margin: .4rem 0 1rem 0; border: 1px solid var(--regla); background: var(--suave); }
.f-veredicto.exacto { border-left: 6px solid var(--petroleo); }
.f-veredicto.roto { border-left: 6px solid var(--naranja); background: #fdf5f1; }
.f-veredicto b { color: var(--tinta); }
/* La cadena del libro */
.cadena { display: flex; flex-wrap: wrap; align-items: stretch; gap: .35rem; margin: .6rem 0 1.2rem 0; }
.eslabon { flex: 1 1 190px; border: 2px solid var(--petroleo); border-radius: 10px; padding: .7rem .8rem; background: #fff; min-width: 170px; }
.eslabon .que { font-size: .74rem; color: var(--grafito); letter-spacing: .01em; }
.eslabon .titulo { font-family: 'IBM Plex Serif', Georgia, serif; font-weight: 600; color: var(--tinta); font-size: 1.02rem; margin: .1rem 0 .25rem 0; }
.eslabon .detalle { font-size: .86rem; color: var(--tinta); line-height: 1.4; }
.eslabon .estado { font-size: .8rem; font-weight: 600; margin-top: .45rem; color: var(--petroleo); }
.eslabon.roto { border: 2px dashed var(--naranja); background: #fdf5f1; }
.eslabon.roto .estado { color: var(--naranja); }
.eslabon.dudoso { border: 2px dashed #b9c4c6; background: #fafbfb; }
.eslabon.dudoso .estado { color: var(--grafito); }
.flecha { align-self: center; color: var(--grafito); font-size: 1.3rem; padding: 0 .1rem; }
@media (max-width: 760px) { .flecha { display: none; } }
.cifra { font-family: 'IBM Plex Serif', Georgia, serif; font-size: 2.6rem; font-weight: 600; color: var(--tinta); line-height: 1.05; }
.cifra.alerta { color: var(--naranja); }
.cifra-etq { font-size: .86rem; color: var(--grafito); }
[data-testid="stMetricValue"] { font-family: 'IBM Plex Serif', Georgia, serif; font-size: 1.65rem; }
[data-testid="stMetricLabel"] p { font-size: .85rem; color: var(--grafito); }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { font-size: 1.02rem !important; margin-top: .7rem !important; }
</style>
"""


def preparar() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(titulo: str, pregunta: str, referencia: str) -> None:
    st.title(titulo)
    st.markdown(f'<p class="f-pregunta">{pregunta}</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="f-ref">Base en el libro: {referencia}</div>', unsafe_allow_html=True)


def nota(t: str) -> None:
    st.markdown(f'<p class="f-nota">{t}</p>', unsafe_allow_html=True)


def veredicto(html: str, exacto: bool | None = None) -> None:
    clase = "" if exacto is None else ("exacto" if exacto else "roto")
    st.markdown(f'<div class="f-veredicto {clase}">{html}</div>', unsafe_allow_html=True)


def cifra(valor: str, etiqueta: str, alerta: bool = False) -> None:
    st.markdown(f'<div class="cifra {"alerta" if alerta else ""}">{valor}</div><div class="cifra-etq">{etiqueta}</div>',
                unsafe_allow_html=True)


def entero(n: int) -> str:
    return f"{int(n):,}".replace(",", " ")


# =====================================================================
# La cadena del libro
# =====================================================================
def cadena(f1: Forma, f2: Forma, cobertura: float | None = None, confianza: float = 0.95) -> None:
    normal = f1.es_normal and f2.es_normal
    roto = "" if normal else "roto"
    dudoso = "" if normal else "dudoso"
    nombres = f1.nombre_corto() if f1 == f2 else f"{f1.nombre_corto()} y {f2.nombre_corto()}"
    e1 = "Ambas poblaciones son normales." if normal else f"Poblaciones: {nombres}. No son normales."
    e4 = (f"El intervalo para σ₂²/σ₁² acierta el {confianza:.0%} de las veces." if normal
          else f"El intervalo ya no acierta el {confianza:.0%} prometido.")
    if cobertura is not None:
        e4 += f" Simulado: {100 * cobertura:.1f} %."
    html = f"""
<div class="cadena">
  <div class="eslabon {roto}"><div class="que">Supuesto</div><div class="titulo">Normalidad</div>
    <div class="detalle">{e1}</div><div class="estado">{"Se cumple" if normal else "Se rompe aquí"}</div></div>
  <div class="flecha">→</div>
  <div class="eslabon {dudoso}"><div class="que">Teorema 7.3, p. 357</div><div class="titulo">(n−1)S²/σ² ~ χ²(n−1)</div>
    <div class="detalle">La varianza muestral, escalada, sigue una chi-cuadrado.</div>
    <div class="estado">{"Exacto" if normal else "Deja de valer"}</div></div>
  <div class="flecha">→</div>
  <div class="eslabon {dudoso}"><div class="que">Definición 7.3, p. 362</div><div class="titulo">(S₁²/σ₁²)/(S₂²/σ₂²) ~ F</div>
    <div class="detalle">El cociente de dos χ² independientes, divididas por sus gl, es una F(n₁−1, n₂−1).</div>
    <div class="estado">{"Exacto" if normal else "Ya no es F"}</div></div>
  <div class="flecha">→</div>
  <div class="eslabon {dudoso}"><div class="que">Ejemplo 7.7 y Ejercicio 8.125</div><div class="titulo">Lo que promete la F</div>
    <div class="detalle">{e4}</div><div class="estado">{"Promesa cumplida" if normal else "Promesa rota"}</div></div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


# =====================================================================
# Controles
# =====================================================================
def selector_forma(prefijo: str, etiqueta: str, defecto: str = "normal", contenedor=None, valor_defecto=None) -> Forma:
    c = contenedor or st.sidebar
    claves = list(FORMAS)
    clave = c.selectbox(etiqueta, claves, index=claves.index(defecto), key=f"{prefijo}_forma",
                        format_func=lambda k: f"{FORMAS[k].nombre}  ({FORMAS[k].familia})")
    e = FORMAS[clave]
    valor = None
    if e.parametro:
        valor = c.number_input(e.etiqueta, float(e.minimo), float(e.maximo),
                               float(valor_defecto if (valor_defecto and clave == defecto) else e.defecto),
                               float(e.paso), key=f"{prefijo}_{clave}_par", format="%.2f")
    f = forma(clave, valor)
    k = f.curtosis()
    ktxt = "∞" if not np.isfinite(k) else f"{k:.2f}"
    c.caption(f"{e.descripcion} Asimetría {f.asimetria():.2f}, curtosis en exceso {ktxt}. Referencia: {e.referencia}.")
    return f


def selector_poblacion(prefijo: str, titulo: str, defecto: str = "normal", sigma: float = 1.0,
                       mostrar_mu: bool = True, valor_defecto=None) -> Poblacion:
    sb = st.sidebar
    sb.subheader(titulo)
    f = selector_forma(prefijo, "Forma", defecto, sb, valor_defecto)
    c1, c2 = sb.columns(2)
    s = c1.number_input("σ (desv. estándar)", 0.01, 1000.0, float(sigma), 0.1, key=f"{prefijo}_sigma", format="%.2f")
    mu = 0.0
    if mostrar_mu:
        mu = c2.number_input("μ (media)", -1000.0, 1000.0, 0.0, 0.5, key=f"{prefijo}_mu", format="%.2f")
    return Poblacion(f, float(s), float(mu))


def costo(esc: motor.Escenario) -> None:
    st.sidebar.markdown(
        f'<div class="f-costo">{entero(esc.B)} pares de muestras: {entero(esc.observaciones())} números aleatorios. '
        f'Solo se guardan S₁² y S₂² de cada par.</div>', unsafe_allow_html=True)


def mostrar_errores(errores: list[str]) -> bool:
    for e in errores:
        st.sidebar.error(e)
    return bool(errores)


# =====================================================================
# Caché y estado
# =====================================================================
@st.cache_resource(show_spinner=False)
def _almacen() -> OrderedDict:
    return OrderedDict()


def cacheado(clave, calcular, maximo: int = 30):
    a = _almacen()
    if clave in a:
        a.move_to_end(clave)
        return a[clave]
    v = calcular()
    a[clave] = v
    while len(a) > maximo:
        a.popitem(last=False)
    return v


def simular(esc: motor.Escenario, progreso=None) -> motor.Resultado:
    return cacheado(("sim", esc), lambda: motor.simular(esc, progreso))


def barra(texto: str = "Simulando…"):
    b = st.progress(0.0, text=texto)
    return b, (lambda fr: b.progress(float(min(max(fr, 0.0), 1.0)), text=texto))


def guardar(prefijo: str, firma, valor) -> None:
    st.session_state[f"{prefijo}_res"] = (firma, valor)


def recuperar(prefijo: str, firma):
    d = st.session_state.get(f"{prefijo}_res")
    if d is None:
        return None, False
    return d[1], d[0] != firma


def aviso_desactualizado() -> None:
    st.info("Cambiaste los controles. Lo que ves corresponde a la última ejecución; pulsa el botón para actualizar.")


def boton(prefijo: str, texto: str = "Ejecutar simulación", deshabilitado: bool = False, lateral: bool = True) -> bool:
    c = st.sidebar if lateral else st
    return c.button(texto, type="primary", use_container_width=True, key=f"{prefijo}_btn", disabled=deshabilitado)


def figura(fig: go.Figure, nombre: str, clave: str) -> None:
    st.plotly_chart(fig, use_container_width=True, key=f"fig_{clave}",
                    config={**gr.CONFIG, "toImageButtonOptions": {"format": "png", "scale": 2, "filename": nombre}})
    st.download_button("Descargar gráfico interactivo (HTML)", fig.to_html(include_plotlyjs="cdn", config=gr.CONFIG),
                       file_name=f"{nombre}.html", mime="text/html", key=f"dl_{clave}")


def tabla_descarga(df: pd.DataFrame, nombre: str, clave: str) -> None:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button("Descargar datos (CSV)", buf.getvalue().encode("utf-8-sig"), file_name=f"{nombre}.csv",
                       mime="text/csv", key=f"dlt_{clave}")
