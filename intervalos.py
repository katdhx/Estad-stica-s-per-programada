"""Fórmulas de los intervalos de confianza de los capítulos 7 y 8.

Todas las funciones son puras y vectorizadas: reciben estadísticos muestrales
(escalares o arreglos de NumPy, uno por réplica) y devuelven los límites
``(L, U)`` del intervalo. Así la misma fórmula sirve para un solo conjunto de
datos (calculadora) y para cien mil réplicas de Monte Carlo.

Notación del libro (Wackerly et al., 7.ª ed.)
---------------------------------------------
- ``z_a``: valor tal que P(Z > z_a) = a (Tabla 4, Apéndice 3; Figura 8.7).
- ``t_a``: valor tal que P(T > t_a) = a (Tabla 5; Sección 7.2, p. 360).
- ``chi2_a``: valor tal que P(chi2 > chi2_a) = a (Tabla 6; Sección 7.2, p. 356).
- ``F_a``: valor tal que P(F > F_a) = a (Tabla 7; Sección 7.2, p. 362).

Es decir, el subíndice es SIEMPRE el área de la cola SUPERIOR. Por eso
``chi2_{1-a/2}`` es el cuantil pequeño y ``chi2_{a/2}`` el grande.

Tipos de intervalo (Sección 8.5, p. 407)
----------------------------------------
- ``"bilateral"``: P(L <= theta <= U) = 1 - alfa.
- ``"inferior"``:  límite de confianza inferior, intervalo [L, +inf).
- ``"superior"``:  límite de confianza superior, intervalo (-inf, U].
"""

from __future__ import annotations

from typing import Literal

import numpy as np
from scipy import stats

Lado = Literal["bilateral", "inferior", "superior"]
LADOS: tuple[str, ...] = ("bilateral", "inferior", "superior")


# =====================================================================
# Valores críticos con la convención de cola superior del libro
# =====================================================================
def z_critico(a: float) -> float:
    """z_a tal que P(Z > z_a) = a."""
    _validar_area(a)
    return float(stats.norm.isf(a))


def t_critico(a: float, gl: float) -> float:
    """t_a con ``gl`` grados de libertad: P(T > t_a) = a."""
    _validar_area(a)
    _validar_gl(gl)
    return float(stats.t.isf(a, gl))


def chi2_critico(a: float, gl: float) -> float:
    """chi2_a con ``gl`` grados de libertad: P(chi2 > chi2_a) = a."""
    _validar_area(a)
    _validar_gl(gl)
    return float(stats.chi2.isf(a, gl))


def f_critico(a: float, gl1: float, gl2: float) -> float:
    """F_a con (gl1, gl2) grados de libertad: P(F > F_a) = a."""
    _validar_area(a)
    _validar_gl(gl1)
    _validar_gl(gl2)
    return float(stats.f.isf(a, gl1, gl2))


def _validar_area(a: float) -> None:
    if not (0 < a < 1):
        raise ValueError(f"El área de cola debe estar en (0, 1); se recibió {a}.")


def _validar_gl(gl: float) -> None:
    if not gl > 0:
        raise ValueError(f"Los grados de libertad deben ser positivos; se recibió {gl}.")


def validar_alfa(alfa: float) -> None:
    if not (0 < alfa < 1):
        raise ValueError("El nivel de confianza 1 - α debe estar estrictamente entre 0 y 1.")


def validar_lado(lado: str) -> None:
    if lado not in LADOS:
        raise ValueError(f"Tipo de intervalo desconocido: {lado!r}. Use uno de {LADOS}.")


def validar_n(n: int, minimo: int = 1, nombre: str = "n") -> None:
    if int(n) != n or n < minimo:
        raise ValueError(f"El tamaño muestral {nombre} debe ser un entero ≥ {minimo}; se recibió {n}.")


# =====================================================================
# Forma general  theta_hat ± c * error estándar   (Ejemplo 8.6; Sección 8.8)
# =====================================================================
def _simetrico(estimador, error_estandar, c_bilateral: float, c_unilateral: float, lado: str):
    est = np.asarray(estimador, dtype=float)
    ee = np.asarray(error_estandar, dtype=float)
    if lado == "bilateral":
        return est - c_bilateral * ee, est + c_bilateral * ee
    if lado == "inferior":
        return est - c_unilateral * ee, np.full_like(est, np.inf)
    return np.full_like(est, -np.inf), est + c_unilateral * ee


# ---------------------------------------------------------------- media
def media_z_sigma(media, sigma: float, n: int, alfa: float, lado: str = "bilateral"):
    """Ȳ ± z_{α/2} σ/√n con σ conocida.

    Pivote Z = (Ȳ - μ)/(σ/√n). Distribución N(0,1) exacta si la población es normal
    (Teorema 7.1) y aproximada para n grande en otro caso (Teorema 7.4, TCL).
    Fórmula general en el Ejemplo 8.6 (Sección 8.6).
    """
    validar_alfa(alfa); validar_lado(lado); validar_n(n)
    if not sigma > 0 or not np.isfinite(sigma):
        raise ValueError("σ debe ser positiva y finita para usar el intervalo Z con σ conocida.")
    ee = sigma / np.sqrt(n)
    return _simetrico(media, ee, z_critico(alfa / 2), z_critico(alfa), lado)


def media_z_s(media, s, n: int, alfa: float, lado: str = "bilateral"):
    """Ȳ ± z_{α/2} S/√n: muestra grande con σ desconocida (Ejemplo 8.7, Sección 8.6)."""
    validar_alfa(alfa); validar_lado(lado); validar_n(n, 2)
    ee = np.asarray(s, dtype=float) / np.sqrt(n)
    return _simetrico(media, ee, z_critico(alfa / 2), z_critico(alfa), lado)


def media_t(media, s, n: int, alfa: float, lado: str = "bilateral"):
    """Ȳ ± t_{α/2, n-1} S/√n (Sección 8.8, Ejemplo 8.11).

    Pivote T = (Ȳ - μ)/(S/√n) ~ t(n-1) exacto bajo normalidad
    (Teoremas 7.1 y 7.3 con la Definición 7.2).
    """
    validar_alfa(alfa); validar_lado(lado); validar_n(n, 2)
    ee = np.asarray(s, dtype=float) / np.sqrt(n)
    return _simetrico(media, ee, t_critico(alfa / 2, n - 1), t_critico(alfa, n - 1), lado)


# ------------------------------------------------------------- varianza
def varianza_chi2(s2, n: int, alfa: float, lado: str = "bilateral"):
    """[(n-1)S²/chi2_{α/2}, (n-1)S²/chi2_{1-α/2}] (Sección 8.9, Ejemplo 8.13).

    Pivote (n-1)S²/σ² ~ chi2(n-1) bajo normalidad (Teorema 7.3).
    Los límites unilaterales corresponden al Ejercicio 8.97.
    """
    validar_alfa(alfa); validar_lado(lado); validar_n(n, 2)
    sc = (n - 1) * np.asarray(s2, dtype=float)
    gl = n - 1
    if lado == "bilateral":
        return sc / chi2_critico(alfa / 2, gl), sc / chi2_critico(1 - alfa / 2, gl)
    if lado == "inferior":
        return sc / chi2_critico(alfa, gl), np.full_like(sc, np.inf)
    return np.full_like(sc, -np.inf), sc / chi2_critico(1 - alfa, gl)


# ------------------------------------------------------------ proporción
def proporcion_wald(p_hat, n: int, alfa: float, lado: str = "bilateral"):
    """p̂ ± z_{α/2} √(p̂(1-p̂)/n) (Sección 8.6, p. 414; Figura 8.8).

    Es el intervalo de muestra grande con el error estándar de la Tabla 8.1
    evaluado en p̂ en lugar de p.
    """
    validar_alfa(alfa); validar_lado(lado); validar_n(n)
    ph = np.asarray(p_hat, dtype=float)
    ee = np.sqrt(ph * (1 - ph) / n)
    return _simetrico(ph, ee, z_critico(alfa / 2), z_critico(alfa), lado)


# ------------------------------------------------------- dos muestras
def dif_medias_z(media1, media2, s2_1, s2_2, n1: int, n2: int, alfa: float, lado: str = "bilateral"):
    """(Ȳ1 - Ȳ2) ± z_{α/2} √(S1²/n1 + S2²/n2) (Tabla 8.1, Ejemplo 8.3, Sección 8.6).

    Si se conocen σ1² y σ2², pueden pasarse en lugar de S1² y S2².
    """
    validar_alfa(alfa); validar_lado(lado); validar_n(n1, 2, "n1"); validar_n(n2, 2, "n2")
    est = np.asarray(media1, dtype=float) - np.asarray(media2, dtype=float)
    ee = np.sqrt(np.asarray(s2_1, dtype=float) / n1 + np.asarray(s2_2, dtype=float) / n2)
    return _simetrico(est, ee, z_critico(alfa / 2), z_critico(alfa), lado)


def varianza_agrupada(s2_1, s2_2, n1: int, n2: int):
    """S_p² = [(n1-1)S1² + (n2-1)S2²]/(n1 + n2 - 2) (Sección 8.8, p. 428)."""
    return ((n1 - 1) * np.asarray(s2_1, dtype=float) + (n2 - 1) * np.asarray(s2_2, dtype=float)) / (
        n1 + n2 - 2
    )


def dif_medias_t(media1, media2, s2_1, s2_2, n1: int, n2: int, alfa: float, lado: str = "bilateral"):
    """(Ȳ1 - Ȳ2) ± t_{α/2, n1+n2-2} S_p √(1/n1 + 1/n2) (Sección 8.8, Ejemplo 8.12).

    Requiere normalidad, muestras independientes y σ1² = σ2².
    """
    validar_alfa(alfa); validar_lado(lado); validar_n(n1, 2, "n1"); validar_n(n2, 2, "n2")
    est = np.asarray(media1, dtype=float) - np.asarray(media2, dtype=float)
    sp = np.sqrt(varianza_agrupada(s2_1, s2_2, n1, n2))
    ee = sp * np.sqrt(1 / n1 + 1 / n2)
    gl = n1 + n2 - 2
    return _simetrico(est, ee, t_critico(alfa / 2, gl), t_critico(alfa, gl), lado)


def dif_proporciones(p1, p2, n1: int, n2: int, alfa: float, lado: str = "bilateral"):
    """(p̂1 - p̂2) ± z_{α/2} √(p̂1q̂1/n1 + p̂2q̂2/n2) (Ejemplo 8.8, Sección 8.6)."""
    validar_alfa(alfa); validar_lado(lado); validar_n(n1, 1, "n1"); validar_n(n2, 1, "n2")
    a = np.asarray(p1, dtype=float)
    b = np.asarray(p2, dtype=float)
    ee = np.sqrt(a * (1 - a) / n1 + b * (1 - b) / n2)
    return _simetrico(a - b, ee, z_critico(alfa / 2), z_critico(alfa), lado)


# ------------------------------------------------- pivotes exactos (8.5)
def exponencial_chi2(suma, n: int, alfa: float, lado: str = "bilateral"):
    """Media θ de una exponencial con el pivote 2ΣY_i/θ ~ chi2(2n).

    Ejercicio 8.47 (y Ejercicio 8.46 para n = 1, que reproduce el Ejemplo 8.4).
    Intervalo: [2ΣY/chi2_{α/2, 2n}, 2ΣY/chi2_{1-α/2, 2n}].
    """
    validar_alfa(alfa); validar_lado(lado); validar_n(n)
    dos_s = 2 * np.asarray(suma, dtype=float)
    gl = 2 * n
    if lado == "bilateral":
        return dos_s / chi2_critico(alfa / 2, gl), dos_s / chi2_critico(1 - alfa / 2, gl)
    if lado == "inferior":
        return dos_s / chi2_critico(alfa, gl), np.full_like(dos_s, np.inf)
    return np.full_like(dos_s, -np.inf), dos_s / chi2_critico(1 - alfa, gl)


def razon_varianzas_f(s2_1, s2_2, n1: int, n2: int, alfa: float, lado: str = "bilateral"):
    """Intervalo para σ2²/σ1² con el pivote F (Definición 7.3; Ejercicio 8.125).

    F = (S1²/σ1²)/(S2²/σ2²) = (σ2²/σ1²)(S1²/S2²) ~ F(n1-1, n2-1). Entonces
    P(F_{1-α/2} ≤ (σ2²/σ1²)(S1²/S2²) ≤ F_{α/2}) = 1 - α y
    σ2²/σ1² ∈ [ (S2²/S1²) F_{1-α/2}, (S2²/S1²) F_{α/2} ].
    """
    validar_alfa(alfa); validar_lado(lado); validar_n(n1, 2, "n1"); validar_n(n2, 2, "n2")
    r = np.asarray(s2_2, dtype=float) / np.asarray(s2_1, dtype=float)
    g1, g2 = n1 - 1, n2 - 1
    if lado == "bilateral":
        return r * f_critico(1 - alfa / 2, g1, g2), r * f_critico(alfa / 2, g1, g2)
    if lado == "inferior":
        return r * f_critico(1 - alfa, g1, g2), np.full_like(r, np.inf)
    return np.full_like(r, -np.inf), r * f_critico(alfa, g1, g2)


# =====================================================================
# Tamaño muestral (Sección 8.7)
# =====================================================================
def n_para_media(sigma: float, B: float, alfa: float) -> int:
    """Menor n con z_{α/2} σ/√n ≤ B (Sección 8.7). Para la Sección 7.2 véase Ej. 7.3."""
    validar_alfa(alfa)
    if not (sigma > 0 and B > 0):
        raise ValueError("σ y el límite B deben ser positivos.")
    return int(np.ceil((z_critico(alfa / 2) * sigma / B) ** 2 - 1e-9))


def n_para_proporcion(p: float, B: float, alfa: float) -> int:
    """Menor n con z_{α/2} √(pq/n) ≤ B (Ejemplo 8.9). Con p = 0.5 se obtiene el máximo."""
    validar_alfa(alfa)
    if not (0 < p < 1 and B > 0):
        raise ValueError("Se necesita 0 < p < 1 y B > 0.")
    return int(np.ceil(z_critico(alfa / 2) ** 2 * p * (1 - p) / B**2 - 1e-9))


def n_para_dif_medias(sigma1: float, sigma2: float, B: float, alfa: float) -> int:
    """n1 = n2 = n con z_{α/2} √(σ1²/n + σ2²/n) ≤ B (Ejemplo 8.10)."""
    validar_alfa(alfa)
    if not (sigma1 > 0 and sigma2 > 0 and B > 0):
        raise ValueError("σ1, σ2 y B deben ser positivos.")
    return int(np.ceil(z_critico(alfa / 2) ** 2 * (sigma1**2 + sigma2**2) / B**2 - 1e-9))


def contiene(L, U, theta: float) -> np.ndarray:
    """Indicador de cobertura 1{L ≤ θ ≤ U}."""
    return (np.asarray(L) <= theta) & (theta <= np.asarray(U))
