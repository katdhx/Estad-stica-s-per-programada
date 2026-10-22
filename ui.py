"""Componentes de interfaz compartidos por todas las páginas (Streamlit)."""

from __future__ import annotations

import io
import json
from collections import OrderedDict
from dataclasses import asdict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from . import graficos as gr
from . import motor
from .poblaciones import ESPECIFICACIONES, Poblacion, crear
from .procedimientos import (
    DOS_MUESTRAS,
    DOS_PROPORCIONES,
    PROCEDIMIENTOS,
    PROPORCION,
    Procedimiento,
)

SIMBOLO = {
    "media_z_sigma": "μ", "media_z_s": "μ", "media_t": "μ", "varianza_chi2": "σ²",
    "exponencial_chi2": "θ", "proporcion_wald": "p", "dif_medias_z": "μ₁ − μ₂",
    "dif_medias_t": "μ₁ − μ₂", "dif_proporciones": "p₁ − p₂", "razon_varianzas_f": "σ₂²/σ₁²",
}

ETIQUETA_LADO = {"bilateral": "Bilateral", "inferior": "Límite inferior", "superior": "Límite superior"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Public+Sans:wght@400;500;600&display=swap');

:root {
  --tinta: #1c2733;
  --grafito: #5a6672;
  --regla: #e6e9ec;
  --pizarra: #2f5d8a;
}
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp td, .stApp th {
  font-family: 'Public Sans', 'Segoe UI', Helvetica, Arial, sans-serif; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stHeading"] h1, [data-testid="stHeading"] h2, [data-testid="stHeading"] h3 {
                 font-family: 'Source Serif 4', 'Source Serif Pro', Cambria, Georgia, 'DejaVu Serif', serif !important; color: var(--tinta);
                 letter-spacing: -0.005em; font-weight: 600 !important; }
h1 { font-size: 2.05rem !important; line-height: 1.2 !important; padding-bottom: 0.1rem !important; }
h2 { font-size: 1.45rem !important; margin-top: 1.6rem !important; }
h3 { font-size: 1.15rem !important; }
.block-container { max-width: 1180px; padding-top: 2.2rem; }
p, li { line-height: 1.6; }
.lab-pregunta { font-family: 'Source Serif 4', 'Source Serif Pro', Cambria, Georgia, 'DejaVu Serif', serif; font-size: 1.12rem; color: var(--grafito);
                max-width: 46rem; margin: 0 0 0.8rem 0; line-height: 1.55; }
.lab-ref { font-size: 0.86rem; color: var(--grafito); border-left: 3px solid var(--pizarra);
           padding: 0.1rem 0 0.1rem 0.7rem; margin: 0.2rem 0 1.2rem 0; }
.lab-nota { font-size: 0.88rem; color: var(--grafito); }
.lab-costo { font-size: 0.84rem; color: var(--grafito); line-height: 1.5; }
.lab-veredicto { border: 1px solid var(--regla); border-radius: 6px; padding: 0.7rem 0.9rem; margin: 0.4rem 0 1rem 0;
                 background: #f6f8f9; }
.lab-veredicto b { color: var(--tinta); }
[data-testid="stMetricValue"] { font-family: 'Source Serif 4', Cambria, Georgia, serif; font-size: 1.7rem; }
[data-testid="stMetricLabel"] p { font-size: 0.85rem; color: var(--grafito); }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { font-size: 1.02rem !important; margin-top: 0.8rem !important; }
.katex { font-size: 1.06em; }
</style>
"""


def preparar() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(titulo: str, pregunta: str, referencia: str) -> None:
    st.title(titulo)
    st.markdown(f'<p class="lab-pregunta">{pregunta}</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="lab-ref">Base en el libro: {referencia}</div>', unsafe_allow_html=True)


def nota(texto: str) -> None:
    st.markdown(f'<p class="lab-nota">{texto}</p>', unsafe_allow_html=True)


def veredicto(html: str) -> None:
    st.markdown(f'<div class="lab-veredicto">{html}</div>', unsafe_allow_html=True)


def fmt(x: float, d: int = 4) -> str:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "∞" if (x is not None and x > 0) else ("−∞" if x is not None else "—")
    return f"{x:.{d}f}"


def entero(n: int) -> str:
    return f"{int(n):,}".replace(",", " ")


# =====================================================================
# Controles
# =====================================================================
def selector_poblacion(prefijo: str, opciones: tuple[str, ...], etiqueta: str = "Población",
                       defecto: str | None = None, contenedor=None) -> Poblacion:
    c = contenedor or st.sidebar
    opciones = tuple(opciones)
    idx = opciones.index(defecto) if defecto in opciones else 0
    clave = c.selectbox(etiqueta, opciones, index=idx, key=f"{prefijo}_pob",
                        format_func=lambda k: ESPECIFICACIONES[k].nombre)
    espec = ESPECIFICACIONES[clave]
    valores = {}
    if espec.parametros:
        cols = c.columns(len(espec.parametros))
        for col, par in zip(cols, espec.parametros):
            valores[par.nombre] = col.number_input(
                par.etiqueta, min_value=float(par.minimo), max_value=float(par.maximo),
                value=float(par.defecto), step=float(par.paso), key=f"{prefijo}_{clave}_{par.nombre}",
                format="%.3f" if par.paso < 0.1 else "%.2f",
            )
    pob = crear(clave, **valores)
    c.caption(f"{espec.descripcion} Referencia: {espec.referencia}.")
    return pob


def selector_escenario(
    prefijo: str,
    procedimientos: tuple[str, ...] | None = None,
    permitir_lado: bool = True,
    n_defecto: int = 30,
    B_defecto: int = 100,
    B_max: int = motor.B_MAXIMO,
    mostrar_n: bool = True,
    mostrar_B: bool = True,
    proc_defecto: str = "media_t",
    pob_defecto: str = "normal",
    mostrar_nivel: bool = True,
) -> tuple[motor.Escenario | None, list[str]]:
    """Bloque de la barra lateral que define un escenario de simulación."""
    sb = st.sidebar
    sb.header("Escenario")
    claves = procedimientos or tuple(PROCEDIMIENTOS.keys())
    idx = claves.index(proc_defecto) if proc_defecto in claves else 0
    clave_proc = sb.selectbox("Procedimiento", claves, index=idx, key=f"{prefijo}_proc",
                              format_func=lambda k: PROCEDIMIENTOS[k].nombre)
    proc: Procedimiento = PROCEDIMIENTOS[clave_proc]
    dos = proc.familia in (DOS_MUESTRAS, DOS_PROPORCIONES)

    sb.subheader("Población" + (" 1" if dos else ""))
    pob1 = selector_poblacion(f"{prefijo}_p1", proc.poblaciones, "Distribución" + (" de la población 1" if dos else ""),
                              pob_defecto if pob_defecto in proc.poblaciones else None)
    pob2 = None
    if dos:
        sb.subheader("Población 2")
        pob2 = selector_poblacion(f"{prefijo}_p2", proc.poblaciones, "Distribución de la población 2",
                                  pob_defecto if pob_defecto in proc.poblaciones else None)

    sb.subheader("Muestreo")
    n1, n2 = n_defecto, None
    if mostrar_n:
        if dos:
            c1, c2 = sb.columns(2)
            n1 = int(c1.number_input("n₁", 1, motor.N_MAXIMO, n_defecto, key=f"{prefijo}_n1"))
            n2 = int(c2.number_input("n₂", 1, motor.N_MAXIMO, n_defecto, key=f"{prefijo}_n2"))
        else:
            n1 = int(sb.number_input("Tamaño de cada muestra n", 1, motor.N_MAXIMO, n_defecto, key=f"{prefijo}_n",
                                     help="Número de observaciones Y₁, …, Yₙ en cada muestra."))
    elif dos:
        n2 = n_defecto
    B = B_defecto
    if mostrar_B:
        B = int(sb.number_input("Número de muestras B", 1, B_max, B_defecto, key=f"{prefijo}_B",
                                help="Cuántas muestras independientes se generan; cada una produce un intervalo."))
    alfa = 0.05
    if mostrar_nivel:
        conf = sb.number_input("Nivel de confianza 1 − α (%)", 50.0, 99.9, 95.0, 0.5, key=f"{prefijo}_conf",
                               format="%.1f")
        alfa = round(1 - conf / 100, 6)
    lado = "bilateral"
    if permitir_lado:
        lado = sb.radio("Tipo de intervalo", list(ETIQUETA_LADO), format_func=ETIQUETA_LADO.get,
                        horizontal=False, key=f"{prefijo}_lado")
    semilla = int(sb.number_input("Semilla aleatoria", 0, 2**31 - 1, 2026, key=f"{prefijo}_semilla",
                                  help="Con la misma semilla y los mismos controles se repite exactamente el experimento."))
    esc = motor.Escenario(procedimiento=clave_proc, pob1=pob1, n1=n1, B=B, alfa=alfa, lado=lado,
                          semilla=semilla, pob2=pob2, n2=n2)
    errores = motor.validar_escenario(esc)
    return esc, errores


def costo(esc: motor.Escenario, contenedor=None) -> None:
    c = contenedor or st.sidebar
    tot = esc.observaciones_totales()
    if esc.proc.familia in (PROPORCION, DOS_PROPORCIONES):
        detalle = ("Para proporciones se genera directamente Y ~ Binomial(n, p) en cada réplica, "
                   "que tiene exactamente la distribución de la suma de n ensayos de Bernoulli (Sección 7.5).")
    else:
        detalle = f"Memoria máxima por lote ≈ {motor.memoria_estimada_mb(max(esc.n1, esc.n2 or 0), esc.B):.1f} MB."
    c.markdown(
        f'<div class="lab-costo">Se generan <b>{entero(esc.B)}</b> muestras de tamaño '
        f'<b>{entero(esc.n1)}</b>{" y " + entero(esc.n2) if esc.n2 else ""}: '
        f'{entero(tot)} números aleatorios. {detalle}</div>',
        unsafe_allow_html=True,
    )


def mostrar_errores(errores: list[str]) -> bool:
    for e in errores:
        st.sidebar.error(e)
    return bool(errores)


# =====================================================================
# Ejecución con caché y estado
# =====================================================================
@st.cache_resource(show_spinner=False)
def _almacen() -> "OrderedDict":
    """Caché propia compartida (LRU). No se usa st.cache_data porque la barra de progreso
    es un elemento de Streamlit creado fuera de la función, y st.cache_data no permite reproducirlo."""
    return OrderedDict()


_MAX_ENTRADAS = 24


def _cacheado(clave, calcular):
    almacen = _almacen()
    if clave in almacen:
        almacen.move_to_end(clave)
        return almacen[clave]
    valor = calcular()
    almacen[clave] = valor
    while len(almacen) > _MAX_ENTRADAS:
        almacen.popitem(last=False)
    return valor


def simular_cache(esc: motor.Escenario, _progreso=None) -> motor.Resultado:
    """Simula el escenario o devuelve el resultado guardado si ya se calculó con los mismos controles."""
    return _cacheado(("simular", esc), lambda: motor.simular(esc, _progreso))


def barrido_cache(esc: motor.Escenario, ns: tuple[int, ...], procs: tuple[str, ...] | None = None,
                  ns2: tuple[int, ...] | None = None, _progreso=None) -> pd.DataFrame:
    clave = ("barrido", esc, tuple(ns), tuple(procs) if procs else None, tuple(ns2) if ns2 else None)
    return _cacheado(clave, lambda: motor.barrido_n(esc, list(ns), _progreso, list(procs) if procs else None,
                                                     list(ns2) if ns2 else None)).copy()


def barra_progreso(texto: str = "Simulando…"):
    barra = st.progress(0.0, text=texto)

    def actualizar(fr: float) -> None:
        barra.progress(float(min(max(fr, 0.0), 1.0)), text=texto)

    return barra, actualizar


def boton_ejecutar(prefijo: str, deshabilitado: bool = False, texto: str = "Ejecutar simulación") -> bool:
    return st.sidebar.button(texto, type="primary", use_container_width=True, key=f"{prefijo}_ejecutar",
                             disabled=deshabilitado)


def guardar(prefijo: str, firma, valor) -> None:
    st.session_state[f"{prefijo}_resultado"] = (firma, valor)


def recuperar(prefijo: str, firma_actual):
    """Devuelve (valor, desactualizado) o (None, False)."""
    dato = st.session_state.get(f"{prefijo}_resultado")
    if dato is None:
        return None, False
    firma, valor = dato
    return valor, firma != firma_actual


def aviso_desactualizado() -> None:
    st.info("Cambiaste los controles. Lo que ves corresponde a la última ejecución; "
            "pulsa «Ejecutar simulación» para actualizar.")


# =====================================================================
# Fichas, descargas, figuras
# =====================================================================
def ficha(proc: Procedimiento, expandida: bool = False) -> None:
    with st.expander(f"Ficha matemática: {proc.nombre}", expanded=expandida):
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("**1. Parámetro**")
            st.markdown(f"${proc.parametro_latex}$: {proc.parametro}")
            st.markdown("**2. Estimador**")
            st.latex(proc.estimador)
            st.markdown("**3. Distribución muestral**")
            st.latex(proc.distribucion_muestral)
            st.markdown("**4. Estadístico pivotal**")
            st.latex(proc.pivote)
            st.markdown("**5. Fórmula del intervalo**")
            st.latex(proc.formula)
            st.caption("Límites unilaterales")
            st.latex(proc.formula_unilateral)
        with c2:
            st.markdown("**6. Supuestos**")
            st.markdown("\n".join(f"- {s}" for s in proc.supuestos))
            st.markdown("**8. Interpretación**")
            st.markdown(proc.interpretacion)
            st.markdown("**9. Referencias en el libro**")
            st.markdown("\n".join(f"- {r}" for r in proc.referencias))
            st.markdown(f"**Tipo de resultado:** {proc.exactitud}.")
        st.markdown("**7. Justificación matemática**")
        st.markdown(proc.justificacion)


def mostrar_figura(fig: go.Figure, nombre: str, clave: str) -> None:
    st.plotly_chart(fig, use_container_width=True, config={**gr.CONFIG, "toImageButtonOptions": {
        "format": "png", "scale": 2, "filename": nombre}}, key=f"fig_{clave}")
    html = fig.to_html(include_plotlyjs="cdn", full_html=True, config=gr.CONFIG)
    st.download_button("Descargar gráfico interactivo (HTML)", html, file_name=f"{nombre}.html",
                       mime="text/html", key=f"dl_fig_{clave}")


def descargar_tabla(df: pd.DataFrame, nombre: str, clave: str, meta: dict | None = None) -> None:
    buf = io.StringIO()
    if meta:
        for k, v in meta.items():
            buf.write(f"# {k}: {v}\n")
    df.to_csv(buf, index=False)
    st.download_button("Descargar datos (CSV)", buf.getvalue().encode("utf-8-sig"), file_name=f"{nombre}.csv",
                       mime="text/csv", key=f"dl_tab_{clave}")


def metadatos(esc: motor.Escenario) -> dict:
    d = {
        "procedimiento": esc.proc.nombre,
        "poblacion_1": esc.pob1.descripcion_corta(),
        "n1": esc.n1,
        "B": esc.B,
        "confianza": f"{1 - esc.alfa:.4f}",
        "tipo": esc.lado,
        "semilla": esc.semilla,
        "parametro_verdadero": esc.parametro_verdadero(),
    }
    if esc.pob2 is not None:
        d["poblacion_2"] = esc.pob2.descripcion_corta()
        d["n2"] = esc.n2
    return d


def configuracion_json(esc: motor.Escenario) -> str:
    """Configuración del experimento para reproducirlo después."""
    return json.dumps(metadatos(esc), ensure_ascii=False, indent=2)
