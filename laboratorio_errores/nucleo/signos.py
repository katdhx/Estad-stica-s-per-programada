"""Extensión opcional: prueba de signos para la mediana.

Supuestos: X1, …, Xn independientes de una población CONTINUA con mediana M.
H0: M = m0. Se cuentan los signos de Xi − m0 (con población continua, P(Xi = m0) = 0;
si en datos reales hay empates con m0, se descartan y n baja).

Bajo H0, cada Xi cae por encima de m0 con probabilidad exactamente 1/2, sea cual sea la
forma de la población. Por independencia,
        Y = #{i : Xi > m0} ~ Binomial(n, 1/2)        bajo H0.
Es la MISMA estructura que la prueba de Jones con p0 = .5: α se calcula con la binomial
y no hace falta suponer normalidad.

Ha: M > m0  → RR = {y ≥ c}  (muchos signos +)
Ha: M < m0  → RR = {y ≤ c}  (pocos signos +)
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from . import binomial as bn

POBLACIONES = {
    "Normal": "Normal con mediana m0 y desviación 1",
    "Exponencial desplazada": "Muy asimétrica: m0 + (E − ln 2), E ~ Exponencial(1)",
    "Cauchy": "Colas pesadísimas, sin media: m0 + Cauchy estándar",
    "Uniforme": "Uniforme en (m0 − 1, m0 + 1)",
}


def generar(poblacion: str, n: int, m0: float, rng: np.random.Generator, size: int = 1,
            desplazamiento: float = 0.0) -> np.ndarray:
    """Muestras de forma (size, n) cuya mediana es m0 + desplazamiento."""
    forma = (size, n)
    centro = m0 + desplazamiento
    if poblacion == "Normal":
        return rng.normal(centro, 1.0, forma)
    if poblacion == "Exponencial desplazada":
        return centro + rng.exponential(1.0, forma) - np.log(2)
    if poblacion == "Cauchy":
        return centro + rng.standard_cauchy(forma)
    if poblacion == "Uniforme":
        return rng.uniform(centro - 1, centro + 1, forma)
    raise ValueError(f"Población desconocida: {poblacion}")


def mediana_teorica(poblacion: str, m0: float) -> float:
    if poblacion not in POBLACIONES:
        raise ValueError(poblacion)
    return m0


def umbral(n: int, alfa_max: float, cola: str) -> int:
    """Umbral entero c con α exacto ≤ alfa_max (la RR más grande posible)."""
    cola_b = "superior" if cola == "superior" else "inferior"
    return bn.umbral_para_alfa(n, 0.5, alfa_max, cola_b)


def prueba(x, m0: float, alfa_max: float, cola: str) -> dict:
    """Aplica la prueba de signos a unos datos."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    dif = x - m0
    usados = dif[dif != 0]
    n = len(usados)
    if n < 1:
        raise ValueError("No quedan observaciones distintas de m0.")
    y = int((usados > 0).sum())
    c = umbral(n, alfa_max, cola)
    alfa_real = bn.alfa(n, 0.5, c, cola)
    if cola == "superior":
        p = float(stats.binom.sf(y - 1, n, 0.5))
        rechaza = y >= c
    else:
        p = float(stats.binom.cdf(y, n, 0.5))
        rechaza = y <= c
    return {"n_usados": n, "empates": int(len(x) - n), "y": y, "c": c, "alfa_real": alfa_real,
            "valor_p": p, "rechaza": bool(rechaza)}


def tasa_rechazo(poblacion: str, n: int, m0: float, alfa_max: float, cola: str, m: int, semilla: int,
                 desplazamiento: float = 0.0) -> tuple[float, float]:
    """Frecuencia de rechazo en m experimentos; con desplazamiento 0 estima α. Devuelve (tasa, α exacto)."""
    rng = np.random.default_rng(semilla)
    x = generar(poblacion, n, m0, rng, size=m, desplazamiento=desplazamiento)
    y = (x > m0).sum(axis=1)
    c = umbral(n, alfa_max, cola)
    rech = y >= c if cola == "superior" else y <= c
    return float(rech.mean()), bn.alfa(n, 0.5, c, cola)
