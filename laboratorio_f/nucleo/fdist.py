"""La distribución F y el intervalo para σ2²/σ1² (capítulos 7 y 8).

Notación del libro: F_a es el valor con área a en la cola SUPERIOR,
P(F > F_a) = a (Tabla 7, Apéndice 3; p. 362). Así, F_a es el cuantil 1 − a.

* Ejemplo 7.7 (p. 363): con n1 = 6, n2 = 10 y σ1² = σ2², P(S1²/S2² ≤ F_.05(5, 9)) = .95.
* Ejercicio 7.29 (p. 367): 1/F ~ F(ν2, ν1), de donde F_{1−a}(ν1, ν2) = 1/F_a(ν2, ν1).
* Intervalo central de la F: P(F_{1−α/2} ≤ F* ≤ F_{α/2}) = 1 − α si F* ~ F(ν1, ν2).
* Ejercicio 8.125 (p. 441): con el pivote F* = (σ2²/σ1²)(S1²/S2²),
      σ2²/σ1² ∈ [ (S2²/S1²) F_{1−α/2},  (S2²/S1²) F_{α/2} ]   con confianza 1 − α.

Observación clave del laboratorio: «el intervalo contiene σ2²/σ1²» y «F* cae en el
intervalo central de la F» son EL MISMO evento escrito de dos formas (método del
pivote, Sección 8.5). Por eso la cobertura del intervalo es exactamente la
probabilidad central del estadístico F*.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def f_critico(a: float, gl1: float, gl2: float) -> float:
    """F_a(gl1, gl2): P(F > F_a) = a."""
    if not 0 < a < 1:
        raise ValueError("El área de cola debe estar en (0, 1).")
    if gl1 <= 0 or gl2 <= 0:
        raise ValueError("Los grados de libertad deben ser positivos.")
    return float(stats.f.isf(a, gl1, gl2))


def _validar_n(n1: int, n2: int) -> None:
    if int(n1) != n1 or int(n2) != n2 or n1 < 2 or n2 < 2:
        raise ValueError("Cada muestra necesita al menos 2 observaciones.")


def intervalo_central(alfa: float, n1: int, n2: int) -> tuple[float, float]:
    """[F_{1−α/2}, F_{α/2}] con ν1 = n1 − 1, ν2 = n2 − 1: contiene a F* con probabilidad 1 − α bajo normalidad."""
    if not 0 < alfa < 1:
        raise ValueError("α debe estar en (0, 1).")
    _validar_n(n1, n2)
    g1, g2 = n1 - 1, n2 - 1
    return f_critico(1 - alfa / 2, g1, g2), f_critico(alfa / 2, g1, g2)


def intervalo_razon(s2_1, s2_2, n1: int, n2: int, alfa: float):
    """IC del 100(1 − α) % para σ2²/σ1² (Ejercicio 8.125). Vectorizado."""
    a, b = intervalo_central(alfa, n1, n2)
    r = np.asarray(s2_2, dtype=float) / np.asarray(s2_1, dtype=float)
    return r * a, r * b


def prob_cola(b: float, gl1: float, gl2: float) -> float:
    """P(F > b) para F ~ F(gl1, gl2)."""
    return float(stats.f.sf(b, gl1, gl2))
