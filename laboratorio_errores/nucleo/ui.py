"""Identidad visual y componentes compartidos.

Misma paleta que la segunda aplicación («Del riesgo a la evidencia»):
azul marino para el texto y H0, rojo para α, azul para β y verde para la potencia.
"""

from __future__ import annotations

import streamlit as st

from . import estado

NAVY = "#0A2540"
GRIS = "#7F8C8D"
GRIS_CLARO = "#D5DBE1"
ALFA = "#C0392B"
BETA = "#2980B9"
POTENCIA = "#27AE60"
FONDO = "#F8F9FA"

CSS = f"""
<style>
.stApp h1, .stApp h2, .stApp h3, [data-testid="stHeading"] h1, [data-testid="stHeading"] h2,
[data-testid="stHeading"] h3 {{ font-family: Georgia, 'Times New Roman', serif !important; color: {NAVY}; }}
.stApp h1 {{ font-size: 2.0rem !important; }}
.stApp h2 {{ font-size: 1.35rem !important; margin-top: 1.4rem !important; }}
.block-container {{ max-width: 1200px; padding-top: 2rem; }}
p, li {{ line-height: 1.6; }}
.pregunta {{ font-size: 1.08rem; color: #4A5568; max-width: 50rem; margin: 0 0 .6rem 0; }}
.ref {{ font-size: .85rem; color: #4A5568; border-left: 3px solid {NAVY}; padding: .1rem 0 .1rem .7rem;
        margin: .2rem 0 1.2rem 0; }}
.caja {{ background: #E8EEF4; border-left: 4px solid {NAVY}; padding: .75rem 1rem; margin: .6rem 0 1rem 0;
         border-radius: 0 6px 6px 0; }}
.caja.aviso {{ background: #FDF2E9; border-left-color: #E67E22; }}
.cifras {{ display: flex; gap: .8rem; flex-wrap: wrap; margin: .4rem 0 1rem 0; }}
.cifra {{ flex: 1 1 125px; border: 1px solid {GRIS_CLARO}; border-top: 5px solid var(--c); border-radius: 6px;
          padding: .55rem .8rem; background: #fff; }}
.cifra .et {{ font-size: .8rem; color: #4A5568; }}
.cifra .v {{ font-family: Georgia, serif; font-size: 1.7rem; color: var(--c); font-weight: 600; line-height: 1.15; }}
.cifra .f {{ font-size: .78rem; color: #4A5568; }}
.etiqueta {{ display: inline-block; padding: .05rem .5rem; border-radius: 4px; color: #fff; font-size: .85rem;
             font-weight: 600; }}
[data-testid="stMetricValue"] {{ font-family: Georgia, serif; }}
[data-testid="stSidebar"] h3 {{ font-size: 1rem !important; }}
</style>
"""


def preparar() -> None:
    estado.inicializar()
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(titulo: str, pregunta: str, referencia: str) -> None:
    st.title(titulo)
    st.markdown(f'<p class="pregunta">{pregunta}</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="ref">Base en el libro: {referencia}</div>', unsafe_allow_html=True)


def caja(html: str, aviso: bool = False) -> None:
    st.markdown(f'<div class="caja{" aviso" if aviso else ""}">{html}</div>', unsafe_allow_html=True)


def cifras(items: list[tuple[str, str, str, str]]) -> None:
    """items = [(etiqueta, valor, fórmula, color)]."""
    html = "".join(
        f'<div class="cifra" style="--c:{c}"><div class="et">{e}</div><div class="v">{v}</div>'
        f'<div class="f">{f}</div></div>' for e, v, f, c in items)
    st.markdown(f'<div class="cifras">{html}</div>', unsafe_allow_html=True)


def etiqueta(texto: str, color: str) -> str:
    return f'<span class="etiqueta" style="background:{color}">{texto}</span>'


def fmt(x: float, d: int = 4) -> str:
    return f"{x:.{d}f}"


def enlace(pagina: str, texto: str) -> None:
    """st.page_link solo funciona dentro de la navegación; en pruebas sueltas se muestra como texto."""
    try:
        st.page_link(pagina, label=texto, icon=":material/arrow_forward:")
    except Exception:  # noqa: BLE001
        st.caption(texto)
