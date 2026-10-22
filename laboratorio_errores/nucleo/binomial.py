"""Prueba binomial del candidato Jones (Sección 10.2).

Planteamiento del libro: Y = número de votantes, entre n = 15, que favorecen a Jones;
Y ~ Binomial(n, p). H0: p = .5 contra Ha: p < .5, con región de rechazo RR = {y ≤ 2}.

Notación de este módulo
-----------------------
n      tamaño de la muestra (número de votantes entrevistados).
p0     valor de p bajo H0.
p1     un valor ESPECÍFICO de p dentro de Ha (el libro usa p = .3).
c      umbral entero de la región de rechazo.
cola   "inferior": Ha: p < p0 y RR = {y ≤ c}   (el caso del libro)
       "superior": Ha: p > p0 y RR = {y ≥ c}

Fórmulas (todas exactas, sin aproximación normal)
------------------------------------------------
α      = P(Y ∈ RR | p = p0)
β(p)   = P(Y ∉ RR | p),  para un p de la alternativa
potencia(p) = 1 − β(p) = P(Y ∈ RR | p)
"""

from __future__ import annotations

import numpy as np
from scipy import stats

COLAS = ("inferior", "superior")


def validar(n: int, p: float, c: int, cola: str) -> None:
    if int(n) != n or n < 1:
        raise ValueError("n debe ser un entero mayor o igual que 1.")
    if not 0 < p < 1:
        raise ValueError("p debe estar estrictamente entre 0 y 1.")
    if cola not in COLAS:
        raise ValueError("cola debe ser 'inferior' o 'superior'.")
    if int(c) != c:
        raise ValueError("El umbral c debe ser entero.")
    if cola == "inferior" and not -1 <= c <= n:
        raise ValueError("Con cola inferior, c debe estar entre −1 (RR vacía) y n.")
    if cola == "superior" and not 0 <= c <= n + 1:
        raise ValueError("Con cola superior, c debe estar entre 0 y n + 1 (RR vacía).")


def en_region(y, c: int, cola: str):
    """True donde y pertenece a la región de rechazo. Vectorizado."""
    y = np.asarray(y)
    return y <= c if cola == "inferior" else y >= c


def prob_rechazo(n: int, p: float, c: int, cola: str = "inferior") -> float:
    """P(Y ∈ RR | p)."""
    validar(n, p, c, cola)
    if cola == "inferior":
        return float(stats.binom.cdf(c, n, p))       # P(Y ≤ c)
    return float(stats.binom.sf(c - 1, n, p))        # P(Y ≥ c) = P(Y > c − 1)


def alfa(n: int, p0: float, c: int, cola: str = "inferior") -> float:
    """Probabilidad de error tipo I: rechazar H0 cuando p = p0."""
    return prob_rechazo(n, p0, c, cola)


def beta(n: int, p: float, c: int, cola: str = "inferior") -> float:
    """Probabilidad de error tipo II en un valor específico p de Ha: no rechazar H0."""
    return 1.0 - prob_rechazo(n, p, c, cola)


def potencia(n: int, p: float, c: int, cola: str = "inferior") -> float:
    return prob_rechazo(n, p, c, cola)


def curva_beta(n: int, c: int, cola: str, ps) -> np.ndarray:
    """β(p) para un arreglo de valores verdaderos p."""
    ps = np.asarray(ps, dtype=float)
    if cola == "inferior":
        return 1.0 - stats.binom.cdf(c, n, ps)
    return 1.0 - stats.binom.sf(c - 1, n, ps)


def pmf(n: int, p: float) -> tuple[np.ndarray, np.ndarray]:
    y = np.arange(n + 1)
    return y, stats.binom.pmf(y, n, p)


def alternativa_valida(p0: float, p1: float, cola: str) -> bool:
    """p1 debe pertenecer a Ha: p1 < p0 (cola inferior) o p1 > p0 (cola superior)."""
    return p1 < p0 if cola == "inferior" else p1 > p0


def umbral_para_alfa(n: int, p0: float, alfa_max: float, cola: str = "inferior") -> int:
    """La región de rechazo más grande con α ≤ alfa_max (con discreta, α exacto suele quedar por debajo)."""
    if cola == "inferior":
        mejor = -1
        for c in range(0, n + 1):
            if alfa(n, p0, c, cola) <= alfa_max:
                mejor = c
        return mejor
    mejor = n + 1
    for c in range(n, -1, -1):
        if alfa(n, p0, c, cola) <= alfa_max:
            mejor = c
    return mejor


def simular(n: int, p: float, c: int, cola: str, m: int, rng: np.random.Generator):
    """m repeticiones del experimento: Y ~ Bin(n, p) y la decisión de rechazar."""
    y = rng.binomial(n, p, size=m)
    return y, en_region(y, c, cola)
