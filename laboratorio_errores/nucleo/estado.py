"""Estado compartido entre páginas.

Los parámetros del ejemplo binomial (b_*) y de la prueba Z (z_*) son los mismos en todos los
módulos: lo que se cambia en el Módulo 1 o 2 es lo que usan el Monte Carlo, el juego de
decisión y la página de Excel.
"""

from __future__ import annotations

import streamlit as st

from . import binomial as bn
from . import pruebaz as pz

_Z = pz.ConfigZ()

DEFAULTS = {
    # Módulo 1: ejemplo de Jones (Sección 10.2)
    "b_n": 15, "b_p0": 0.50, "b_p1": 0.30, "b_c": 2, "b_cola": "inferior", "b_m": 10000,
    # Módulo 2: prueba Z
    "z_mu0": _Z.mu0, "z_mu1": _Z.mu1, "z_sigma": _Z.sigma, "z_n": _Z.n, "z_alfa": _Z.alfa, "z_cola": _Z.cola,
    "z_modo": "Fijo α y calculo la frontera", "z_beta_obj": 0.10,
    # Módulo 3: Monte Carlo
    "mc_prueba": "Prueba Z (Módulo 2)", "mc_m": 5000, "mc_escenario": "Mitad H0, mitad Ha", "mc_semilla": 2026,
    # Módulo 4: decisión
    "d_prueba": "Prueba Z (Módulo 2)",
    # Extensión: signos
    "s_pob": "Exponencial desplazada", "s_n": 20, "s_alfa": 0.05, "s_cola": "superior", "s_m": 20000,
}


def inicializar() -> None:
    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


def conservar() -> None:
    """Truco de Streamlit: reasignar las claves evita que se borren al cambiar de página."""
    for k in DEFAULTS:
        if k in st.session_state:
            st.session_state[k] = st.session_state[k]
    for k in ("z_k", "x_mu0", "x_sigma", "x_alfa", "x_cola", "x_col"):
        if k in st.session_state:
            st.session_state[k] = st.session_state[k]


def config_z() -> pz.ConfigZ:
    s = st.session_state
    return pz.ConfigZ(float(s.z_mu0), float(s.z_mu1), float(s.z_sigma), int(s.z_n), float(s.z_alfa), s.z_cola)


def binom() -> dict:
    s = st.session_state
    return {"n": int(s.b_n), "p0": float(s.b_p0), "p1": float(s.b_p1), "c": int(s.b_c), "cola": s.b_cola}


def z_valida() -> tuple[bool, str]:
    try:
        config_z().validar()
        return True, ""
    except ValueError as e:
        return False, str(e)


def binom_valida() -> tuple[bool, str]:
    b = binom()
    try:
        bn.validar(b["n"], b["p0"], b["c"], b["cola"])
        bn.validar(b["n"], b["p1"], b["c"], b["cola"])
    except ValueError as e:
        return False, str(e)
    if not bn.alternativa_valida(b["p0"], b["p1"], b["cola"]):
        signo = "<" if b["cola"] == "inferior" else ">"
        return False, f"p₁ debe pertenecer a Hₐ: p {signo} p₀. Ahora p₁ = {b['p1']:.2f} y p₀ = {b['p0']:.2f}."
    return True, ""


def aplicar_z(cfg: pz.ConfigZ) -> None:
    """Carga una configuración Z (desde JSON o Excel). Úsese dentro de un callback."""
    s = st.session_state
    s.z_mu0, s.z_mu1, s.z_sigma = float(cfg.mu0), float(cfg.mu1), float(cfg.sigma)
    s.z_n, s.z_alfa, s.z_cola = int(cfg.n), float(cfg.alfa), cfg.cola
    s.z_modo = DEFAULTS["z_modo"]
    s.pop("z_k", None)


def aplicar_binom(d: dict) -> None:
    s = st.session_state
    s.b_n, s.b_p0, s.b_p1, s.b_c, s.b_cola = int(d["n"]), float(d["p0"]), float(d["p1"]), int(d["c"]), d["cola"]
