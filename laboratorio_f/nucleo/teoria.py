"""Resultados teóricos para comparar con la simulación.

Del libro
---------
* Densidad F(ν1, ν2) (Definición 7.3; su fórmula está en el Ejercicio 7.99).
* E(F) = ν2/(ν2 − 2) si ν2 > 2;
  V(F) = 2ν2²(ν1 + ν2 − 2) / [ν1(ν2 − 2)²(ν2 − 4)] si ν2 > 4 (Ejercicio 7.34, p. 362).
* E(χ²_ν) = ν, V(χ²_ν) = 2ν.

Complementario (derivado con herramientas del curso, no está en los caps. 7 y 8)
-------------------------------------------------------------------------------
* Varianza de S² para cualquier población con cuarto momento finito:
      V(S²) = σ⁴ [ 2/(n − 1) + κ/n ],   κ = curtosis en exceso.
  Se obtiene desarrollando E[(Σ(Yi − Ȳ)²)²] con los teoremas de valores esperados
  del capítulo 5. Con κ = 0 (normal) da 2σ⁴/(n − 1), que es V(χ²_{n−1})·σ⁴/(n − 1)².
* Aproximación de la cobertura real para n grande:
  S_i²/σ² ≈ N(1, v_i) con v_i = 2/(n_i − 1) + κ_i/n_i (TCL aplicado a los cuadrados),
  de modo que F* ≈ 1 + (desviación normal con varianza v1 + v2), mientras que los
  cuantiles de la F suponen κ1 = κ2 = 0 (v_ref). Comparando ambas varianzas:
      cobertura ≈ 2Φ(z_{α/2} √(v_ref/v_real)) − 1
  Con n1 = n2 grande y la misma forma en ambas poblaciones, v_ref/v_real → 2/(2 + κ).
"""

from __future__ import annotations

import numpy as np
from scipy import stats

from .poblaciones import Forma


def densidad_f(gl1: float, gl2: float):
    return stats.f(gl1, gl2).pdf


def media_f(gl2: float) -> float:
    return gl2 / (gl2 - 2) if gl2 > 2 else float("inf")


def varianza_f(gl1: float, gl2: float) -> float:
    if gl2 <= 4:
        return float("inf")
    return 2 * gl2**2 * (gl1 + gl2 - 2) / (gl1 * (gl2 - 2) ** 2 * (gl2 - 4))


def varianza_s2(sigma2: float, n: int, curtosis: float) -> float:
    """V(S²) = σ⁴[2/(n−1) + κ/n] (complementario)."""
    return sigma2**2 * (2 / (n - 1) + curtosis / n)


def varianza_w(n: int, curtosis: float) -> float:
    """V(W) para W = (n − 1)S²/σ²: (n − 1)²[2/(n − 1) + κ/n]. Con κ = 0 da 2(n − 1) = V(χ²_{n−1})."""
    return (n - 1) ** 2 * (2 / (n - 1) + curtosis / n)


def cobertura_aproximada(f1: Forma, f2: Forma, n1: int, n2: int, alfa: float) -> float:
    """Cobertura real aproximada del intervalo de 8.125 (o probabilidad central de F*) para n grande (complementario)."""
    k1, k2 = f1.curtosis(), f2.curtosis()
    if not (np.isfinite(k1) and np.isfinite(k2)):
        return 0.0
    v_ref = 2 / (n1 - 1) + 2 / (n2 - 1)
    v_real = 2 / (n1 - 1) + k1 / n1 + 2 / (n2 - 1) + k2 / n2
    if v_real <= 0:
        return 1.0
    z = stats.norm.isf(alfa / 2)
    return float(1 - 2 * stats.norm.sf(z * np.sqrt(v_ref / v_real)))


def cobertura_limite(curtosis: float, alfa: float) -> float:
    """Límite n1 = n2 → ∞, misma forma en las dos poblaciones: 2Φ(z_{α/2}√(2/(2+κ))) − 1 (complementario)."""
    if not np.isfinite(curtosis):
        return 0.0
    z = stats.norm.isf(alfa / 2)
    return float(1 - 2 * stats.norm.sf(z * np.sqrt(2 / (2 + curtosis))))


def ks_distancia(muestra: np.ndarray, gl1: float, gl2: float) -> float:
    """Distancia de Kolmogorov entre la F empírica y la F(ν1, ν2): máx |F̂(x) − F(x)|."""
    return float(stats.kstest(muestra, stats.f(gl1, gl2).cdf).statistic)


def cola_superior_limite(curtosis: float, a: float) -> float:
    """Límite n1 = n2 → ∞ de P(F* > F_a), misma forma en las dos poblaciones (complementario)."""
    if not np.isfinite(curtosis):
        return 0.5
    return float(stats.norm.sf(stats.norm.isf(a) * np.sqrt(2 / (2 + curtosis))))
