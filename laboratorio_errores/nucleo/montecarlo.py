"""Experimento Monte Carlo: repetir la prueba muchas veces y contar errores.

Cada experimento simulado:
  1. decide cuál es el estado verdadero (H0 o la alternativa específica),
  2. genera una muestra completa,
  3. calcula el estadístico de prueba,
  4. aplica la regla de rechazo,
  5. clasifica: error tipo I, error tipo II o decisión correcta.

Frecuencia empírica de error tipo I = (# rechazos entre los experimentos con H0 verdadera)
                                       / (# experimentos con H0 verdadera).
Error Monte Carlo (error estándar de una proporción): √(p̂(1 − p̂)/m).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import binomial as bn
from . import pruebaz as pz

H0_V = "H0 verdadera"
HA_V = "Ha verdadera"
RECHAZA = "Rechazar H0"
NO_RECHAZA = "No rechazar H0"
ERR1 = "Error tipo I"
ERR2 = "Error tipo II"
OK = "Decisión correcta"

BLOQUE = 4000  # experimentos por bloque, para no llenar la memoria con muestras grandes


def _estados(m: int, prob_h0: float, rng: np.random.Generator) -> np.ndarray:
    if not 0 <= prob_h0 <= 1:
        raise ValueError("La proporción de experimentos con H0 verdadera debe estar en [0, 1].")
    return rng.random(m) < prob_h0


def _clasificar(h0_verdadera: np.ndarray, rechaza: np.ndarray) -> np.ndarray:
    res = np.full(h0_verdadera.shape, OK, dtype=object)
    res[h0_verdadera & rechaza] = ERR1
    res[~h0_verdadera & ~rechaza] = ERR2
    return res


def simular_z(cfg: pz.ConfigZ, m: int, prob_h0: float, semilla: int) -> pd.DataFrame:
    """m experimentos de la prueba Z. Cada uno genera n observaciones normales."""
    cfg.validar()
    if m < 1:
        raise ValueError("Se necesita al menos un experimento.")
    rng = np.random.default_rng(semilla)
    h0 = _estados(m, prob_h0, rng)
    mu = np.where(h0, cfg.mu0, cfg.mu1)
    medias = np.empty(m)
    for i in range(0, m, BLOQUE):
        j = min(i + BLOQUE, m)
        muestra = rng.normal(mu[i:j, None], cfg.sigma, size=(j - i, cfg.n))
        medias[i:j] = muestra.mean(axis=1)
    z = pz.estadistico(medias, cfg)
    rechaza = pz.rechaza_z(z, cfg)
    return pd.DataFrame({
        "experimento": np.arange(1, m + 1),
        "estado": np.where(h0, H0_V, HA_V),
        "media_muestral": medias,
        "z": z,
        "decision": np.where(rechaza, RECHAZA, NO_RECHAZA),
        "resultado": _clasificar(h0, rechaza),
    })


def simular_binomial(n: int, p0: float, p1: float, c: int, cola: str, m: int, prob_h0: float,
                     semilla: int) -> pd.DataFrame:
    """m experimentos de la prueba binomial: Y ~ Bin(n, p0) o Bin(n, p1)."""
    bn.validar(n, p0, c, cola)
    bn.validar(n, p1, c, cola)
    rng = np.random.default_rng(semilla)
    h0 = _estados(m, prob_h0, rng)
    y = rng.binomial(n, np.where(h0, p0, p1))
    rechaza = bn.en_region(y, c, cola)
    return pd.DataFrame({
        "experimento": np.arange(1, m + 1),
        "estado": np.where(h0, H0_V, HA_V),
        "y": y,
        "decision": np.where(rechaza, RECHAZA, NO_RECHAZA),
        "resultado": _clasificar(h0, rechaza),
    })


def error_mc(p: float, m: int) -> float:
    return float(np.sqrt(p * (1 - p) / m)) if m > 0 else float("nan")


def resumen(df: pd.DataFrame, alfa_teo: float, beta_teo: float) -> pd.DataFrame:
    """Tabla teórico vs empírico, con el error Monte Carlo."""
    filas = []
    for nombre, estado, error, teo in (("Error tipo I (α)", H0_V, ERR1, alfa_teo),
                                       ("Error tipo II (β)", HA_V, ERR2, beta_teo)):
        sub = df[df["estado"] == estado]
        m = len(sub)
        if m == 0:
            continue
        p = float((sub["resultado"] == error).mean())
        ee = error_mc(teo, m)
        filas.append({
            "Probabilidad": nombre,
            "Experimentos con ese estado": m,
            "Teórica": teo,
            "Frecuencia empírica": p,
            "Error Monte Carlo": error_mc(p, m),
            "Diferencia / EE teórico": (p - teo) / ee if ee > 0 else float("nan"),
        })
    return pd.DataFrame(filas)


def trayectoria(df: pd.DataFrame, estado: str, error: str) -> pd.DataFrame:
    """Frecuencia acumulada del error conforme se agregan experimentos con ese estado verdadero."""
    sub = df[df["estado"] == estado]
    if sub.empty:
        return pd.DataFrame(columns=["m", "frecuencia"])
    aciertos = (sub["resultado"] == error).to_numpy().astype(float)
    m = np.arange(1, len(aciertos) + 1)
    return pd.DataFrame({"m": m, "frecuencia": np.cumsum(aciertos) / m})
