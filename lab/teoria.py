"""Resultados teóricos para comparar con la simulación.

Se distinguen dos tipos de resultado, y la interfaz los etiqueta así:

* **Del libro**: consecuencias directas de los teoremas de los capítulos 7 y 8
  (p. ej., la amplitud 2 z σ/√n, o que (n−1)S²/σ² ~ χ²(n−1)).
* **Complementario**: derivaciones propias a partir de esos teoremas, que el
  libro no presenta pero que se obtienen con las herramientas del curso. Por
  ejemplo, E(S) bajo normalidad (con el Teorema 7.3 y los momentos de la gamma
  del capítulo 4), o la cobertura exacta del intervalo de Wald sumando
  probabilidades binomiales (Sección 3.4).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import special, stats

from . import intervalos as ic
from .poblaciones import Poblacion


# =====================================================================
# Constante c4(n) = E(S)/σ bajo normalidad
# =====================================================================
def c4(n: int | np.ndarray) -> np.ndarray:
    """E(S)/σ para una muestra normal de tamaño n.

    Derivación (complementaria): por el Teorema 7.3, S = σ √(W/(n−1)) con
    W ~ χ²(n−1) = Gamma(α = (n−1)/2, β = 2). Usando E(W^{1/2}) = 2^{1/2} Γ(n/2)/Γ((n−1)/2)
    se obtiene c4(n) = √(2/(n−1)) · Γ(n/2)/Γ((n−1)/2). Se calcula con logaritmos de
    la función gamma para que funcione con n = 100 000.
    """
    n = np.asarray(n, dtype=float)
    return np.sqrt(2.0 / (n - 1)) * np.exp(special.gammaln(n / 2) - special.gammaln((n - 1) / 2))


@dataclass(frozen=True)
class Teorico:
    valor: float | None
    exacto: bool
    nota: str


def amplitud_esperada(
    procedimiento: str, pob1: Poblacion, n1: int, alfa: float,
    pob2: Poblacion | None = None, n2: int | None = None,
) -> Teorico:
    """E(amplitud) de un intervalo bilateral, con una nota sobre su validez."""
    z = ic.z_critico(alfa / 2)
    if procedimiento == "media_z_sigma":
        return Teorico(2 * z * pob1.desviacion() / np.sqrt(n1), True,
                       "A = 2 z_{α/2} σ/√n no es aleatoria (Sección 8.6).")
    if procedimiento in ("media_z_s", "media_t"):
        crit = z if procedimiento == "media_z_s" else ic.t_critico(alfa / 2, n1 - 1)
        if pob1.espec.es_normal:
            return Teorico(2 * crit * pob1.desviacion() * float(c4(n1)) / np.sqrt(n1), True,
                           "E(A) = 2·c·σ·c4(n)/√n con E(S) = σ·c4(n) (complementario, a partir del Teorema 7.3).")
        if not pob1.varianza_finita():
            return Teorico(None, False, "σ² = ∞: la amplitud no se estabiliza.")
        return Teorico(2 * crit * pob1.desviacion() / np.sqrt(n1), False,
                       "Aproximación E(S) ≈ σ (válida para n grande; la población no es normal).")
    if procedimiento == "varianza_chi2":
        if not pob1.varianza_finita():
            return Teorico(None, False, "σ² = ∞.")
        g = n1 - 1
        v = g * pob1.varianza() * (1 / ic.chi2_critico(1 - alfa / 2, g) - 1 / ic.chi2_critico(alfa / 2, g))
        return Teorico(v, True, "E(A) = (n−1)σ²(1/χ²_{1−α/2} − 1/χ²_{α/2}). Vale para cualquier población porque E(S²) = σ² (Ejemplo 8.1).")
    if procedimiento == "exponencial_chi2":
        g = 2 * n1
        v = 2 * n1 * pob1.media() * (1 / ic.chi2_critico(1 - alfa / 2, g) - 1 / ic.chi2_critico(alfa / 2, g))
        return Teorico(v, True, "E(A) = 2nθ(1/χ²_{1−α/2,2n} − 1/χ²_{α/2,2n}) porque E(ΣYᵢ) = nθ.")
    if procedimiento == "proporcion_wald":
        p = pob1.media()
        return Teorico(2 * z * np.sqrt(p * (1 - p) / n1), False,
                       "Aproximación de primer orden: 2 z_{α/2} √(pq/n), con p en lugar de p̂.")
    if procedimiento == "dif_medias_z":
        return Teorico(2 * z * np.sqrt(pob1.varianza() / n1 + pob2.varianza() / n2), False,
                       "Aproximación: 2 z_{α/2} √(σ₁²/n₁ + σ₂²/n₂).")
    if procedimiento == "dif_medias_t":
        g = n1 + n2 - 2
        t = ic.t_critico(alfa / 2, g)
        raiz = np.sqrt(1 / n1 + 1 / n2)
        if pob1.espec.es_normal and pob2.espec.es_normal and np.isclose(pob1.varianza(), pob2.varianza()):
            return Teorico(2 * t * pob1.desviacion() * float(c4(g + 1)) * raiz, True,
                           "E(S_p) = σ·c4(n₁+n₂−1) bajo normalidad y varianzas iguales (complementario).")
        sp2 = ((n1 - 1) * pob1.varianza() + (n2 - 1) * pob2.varianza()) / g
        return Teorico(2 * t * np.sqrt(sp2) * raiz, False, "Aproximación con E(S_p²) en lugar de E(S_p).")
    if procedimiento == "dif_proporciones":
        p1, p2 = pob1.media(), pob2.media()
        return Teorico(2 * z * np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2), False,
                       "Aproximación de primer orden.")
    if procedimiento == "razon_varianzas_f":
        g1, g2 = n1 - 1, n2 - 1
        if pob1.espec.es_normal and pob2.espec.es_normal and g1 > 2:
            r = pob2.varianza() / pob1.varianza()
            v = r * g1 / (g1 - 2) * (ic.f_critico(alfa / 2, g1, g2) - ic.f_critico(1 - alfa / 2, g1, g2))
            return Teorico(v, True, "E(1/S₁²) = (n₁−1)/[(n₁−3)σ₁²] bajo normalidad (complementario).")
        return Teorico(None, False, "Sin expresión cerrada fuera de la normalidad.")
    return Teorico(None, False, "")


def de_amplitud_t(pob: Poblacion, n: int, alfa: float, procedimiento: str = "media_t") -> float | None:
    """Desviación estándar de la amplitud de los intervalos t o Z-con-S (normalidad)."""
    if not pob.espec.es_normal:
        return None
    crit = ic.t_critico(alfa / 2, n - 1) if procedimiento == "media_t" else ic.z_critico(alfa / 2)
    return float(2 * crit * pob.desviacion() * np.sqrt(1 - c4(n) ** 2) / np.sqrt(n))


def error_estandar_estimador(procedimiento: str, pob: Poblacion, n: int) -> float | None:
    """Error estándar teórico del estimador puntual (Tabla 8.1 y Teorema 7.3)."""
    if procedimiento in ("media_z_sigma", "media_z_s", "media_t", "exponencial_chi2", "proporcion_wald"):
        v = pob.varianza()
        return float(np.sqrt(v / n)) if np.isfinite(v) else None
    if procedimiento == "varianza_chi2" and pob.espec.es_normal:
        # V(S²) = 2σ⁴/(n−1), porque V(χ²_ν) = 2ν (Teorema 7.3)
        return float(np.sqrt(2 * pob.varianza() ** 2 / (n - 1)))
    return None


# =====================================================================
# Coberturas teóricas
# =====================================================================
def cobertura_exacta_wald(n: int, p: float, alfa: float, lado: str = "bilateral") -> float:
    """Cobertura EXACTA del intervalo de Wald (complementario).

    C(p) = Σ_{y=0}^{n} P(Y = y) · 1{p ∈ IC(y)}, con Y ~ Binomial(n, p).
    No es una simulación: es una suma finita de probabilidades binomiales.
    """
    y = np.arange(n + 1)
    L, U = ic.proporcion_wald(y / n, n, alfa, lado)
    dentro = (L <= p) & (p <= U)
    return float(stats.binom.pmf(y, n, p)[dentro].sum())


def cobertura_exacta_wald_curva(n: int, ps: np.ndarray, alfa: float) -> np.ndarray:
    y = np.arange(n + 1)
    L, U = ic.proporcion_wald(y / n, n, alfa, "bilateral")
    ps = np.asarray(ps, dtype=float)
    pmf = stats.binom.pmf(y[None, :], n, ps[:, None])
    dentro = (L[None, :] <= ps[:, None]) & (ps[:, None] <= U[None, :])
    return (pmf * dentro).sum(axis=1)


def cobertura_limite_chi2(curtosis_exceso: float, alfa: float) -> float:
    """Cobertura asintótica del intervalo χ² para σ² en una población NO normal (complementario).

    Si κ es la curtosis en exceso, para n grande (n−1)S²/σ² ≈ N(n−1, (n−1)(2 + κ)),
    mientras que los cuantiles χ²(n−1) se comportan como (n−1) ± z√(2(n−1)). Por eso
    la cobertura tiende a 2Φ(z_{α/2} √(2/(2 + κ))) − 1, que es 1 − α solo si κ = 0.
    """
    if not np.isfinite(curtosis_exceso):
        return 0.0
    z = ic.z_critico(alfa / 2)
    return float(2 * stats.norm.cdf(z * np.sqrt(2 / (2 + curtosis_exceso))) - 1)


def cobertura_exacta_z_s_normal(n: int, alfa: float) -> float:
    """Cobertura exacta del intervalo Ȳ ± z S/√n bajo normalidad: P(|T_{n−1}| ≤ z_{α/2})."""
    z = ic.z_critico(alfa / 2)
    return float(stats.t.cdf(z, n - 1) - stats.t.cdf(-z, n - 1))


def regla_binomial(n: int, p: float) -> bool:
    """Regla del libro: p ± 3√(pq/n) ∈ (0, 1) (Sección 7.5, p. 380)."""
    d = 3 * np.sqrt(p * (1 - p) / n)
    return bool(0 < p - d and p + d < 1)


def regla_binomial_alternativa(n: int, p: float) -> bool:
    """n > 9·(mayor de p y q)/(menor de p y q) (Ejercicio 7.70, p. 380)."""
    q = 1 - p
    return bool(n > 9 * max(p, q) / min(p, q))


# =====================================================================
# Distribuciones teóricas de los estadísticos (Experimento 5)
# =====================================================================
def densidad_media_exacta(pob: Poblacion, n: int):
    """Densidad EXACTA de Ȳ cuando se conoce en forma cerrada.

    - Normal: N(μ, σ²/n) (Teorema 7.1).
    - Exponencial(θ): ΣYᵢ ~ Gamma(n, θ), así que Ȳ ~ Gamma(α = n, β = θ/n) (FGM, Sección 6.5).
    - Gamma(α, β): Ȳ ~ Gamma(nα, β/n) (FGM, Sección 6.5).
    Devuelve ``None`` en los demás casos.
    """
    p = pob.p
    if pob.clave == "normal":
        return stats.norm(p["mu"], p["sigma"] / np.sqrt(n)).pdf
    if pob.clave == "exponencial":
        return stats.gamma(n, scale=p["theta"] / n).pdf
    if pob.clave == "gamma":
        return stats.gamma(n * p["alpha"], scale=p["beta"] / n).pdf
    return None
