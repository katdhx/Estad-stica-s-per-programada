"""Motor de Monte Carlo para el estadístico F.

Para cada réplica b = 1, …, B se generan dos muestras independientes,
Y11, …, Y1n1 de la población 1 y Y21, …, Y2n2 de la población 2, y se guardan sus
varianzas muestrales S1² y S2² (divisor n − 1). Con ellas se forman:

* W1 = (n1 − 1)S1²/σ1² y W2 = (n2 − 1)S2²/σ2²  → χ² bajo normalidad (Teorema 7.3);
* F* = (S1²/σ1²)/(S2²/σ2²)                      → F(n1−1, n2−1) bajo normalidad (Def. 7.3);
* S1²/S2²                                        → el cociente del Ejemplo 7.7 (igual a F* si σ1² = σ2²).

Las observaciones se generan por lotes (a lo sumo ``MAX_LOTE`` números) y no se
guardan: solo sobreviven S1² y S2². Cada población usa su propio generador hijo
de la semilla, así que las dos muestras son independientes y el resultado es
reproducible y no depende del tamaño del lote.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from . import fdist as fd
from .poblaciones import Forma, Poblacion

MAX_LOTE = 4_000_000
LIMITE_OBS = 300_000_000
N_MAX = 20_000
B_MAX = 200_000

Progreso = Callable[[float], None] | None


class ErrorSimulacion(ValueError):
    pass


@dataclass(frozen=True)
class Escenario:
    pob1: Poblacion
    pob2: Poblacion
    n1: int
    n2: int
    B: int
    semilla: int = 2026

    def validar(self) -> list[str]:
        e = [f"Población 1: {m}" for m in self.pob1.validar()]
        e += [f"Población 2: {m}" for m in self.pob2.validar()]
        for nombre, n in (("n₁", self.n1), ("n₂", self.n2)):
            if int(n) != n or n < 2:
                e.append(f"{nombre} debe ser un entero ≥ 2 (S² necesita al menos dos datos).")
            elif n > N_MAX:
                e.append(f"{nombre} no puede pasar de {N_MAX:,}.".replace(",", " "))
        if int(self.B) != self.B or self.B < 1:
            e.append("B debe ser un entero ≥ 1.")
        elif self.B > B_MAX:
            e.append(f"B no puede pasar de {B_MAX:,}.".replace(",", " "))
        if not e and self.observaciones() > LIMITE_OBS:
            e.append(f"La simulación pediría {self.observaciones():,} números (B × (n₁ + n₂)); el límite es "
                     f"{LIMITE_OBS:,}. Reduce B o los tamaños.".replace(",", " "))
        return e

    def observaciones(self) -> int:
        return int(self.B) * (int(self.n1) + int(self.n2))

    @property
    def gl(self) -> tuple[int, int]:
        return self.n1 - 1, self.n2 - 1

    @property
    def razon_verdadera(self) -> float:
        """σ1²/σ2²."""
        return self.pob1.varianza / self.pob2.varianza

    @property
    def f_exacta(self) -> bool:
        """¿F* sigue exactamente una F(n1−1, n2−1)? Solo si ambas poblaciones son normales."""
        return self.pob1.forma.es_normal and self.pob2.forma.es_normal


def _varianzas(pob: Poblacion, n: int, B: int, rng: np.random.Generator,
               progreso: Progreso, a: float, b: float) -> np.ndarray:
    filas = int(max(1, min(B, MAX_LOTE // n)))
    s2 = np.empty(B)
    i = 0
    while i < B:
        j = min(B, i + filas)
        X = pob.muestrear(rng, (j - i, n))
        s2[i:j] = X.var(axis=1, ddof=1)
        i = j
        if progreso is not None:
            progreso(a + (b - a) * i / B)
    return s2


@dataclass
class Resultado:
    escenario: Escenario
    s2_1: np.ndarray
    s2_2: np.ndarray
    segundos: float = 0.0

    @property
    def W1(self) -> np.ndarray:
        return (self.escenario.n1 - 1) * self.s2_1 / self.escenario.pob1.varianza

    @property
    def W2(self) -> np.ndarray:
        return (self.escenario.n2 - 1) * self.s2_2 / self.escenario.pob2.varianza

    @property
    def F_pivote(self) -> np.ndarray:
        """F* = (S1²/σ1²)/(S2²/σ2²)."""
        return (self.s2_1 / self.escenario.pob1.varianza) / (self.s2_2 / self.escenario.pob2.varianza)

    @property
    def F_cociente(self) -> np.ndarray:
        """S1²/S2², el cociente del Ejemplo 7.7 y el Ejercicio 7.27."""
        return self.s2_1 / self.s2_2

    def tabla(self) -> pd.DataFrame:
        return pd.DataFrame({
            "replica": np.arange(1, len(self.s2_1) + 1),
            "S1_2": self.s2_1, "S2_2": self.s2_2,
            "W1": self.W1, "W2": self.W2,
            "F_pivote": self.F_pivote, "F_cociente": self.F_cociente,
        })


def simular(esc: Escenario, progreso: Progreso = None) -> Resultado:
    errores = esc.validar()
    if errores:
        raise ErrorSimulacion(" ".join(errores))
    t0 = time.perf_counter()
    r1, r2 = (np.random.default_rng(s) for s in np.random.SeedSequence(esc.semilla).spawn(2))
    peso = esc.n1 / (esc.n1 + esc.n2)
    s1 = _varianzas(esc.pob1, esc.n1, esc.B, r1, progreso, 0.0, peso)
    s2 = _varianzas(esc.pob2, esc.n2, esc.B, r2, progreso, peso, 1.0)
    return Resultado(esc, s1, s2, time.perf_counter() - t0)


def muestras_ejemplo(esc: Escenario, semilla: int) -> tuple[np.ndarray, np.ndarray]:
    """Un par de muestras concretas, para la vista «anatomía de una réplica»."""
    r1, r2 = (np.random.default_rng(s) for s in np.random.SeedSequence(semilla).spawn(2))
    return esc.pob1.muestrear(r1, (esc.n1,)), esc.pob2.muestrear(r2, (esc.n2,))


# =====================================================================
# Cobertura y probabilidades de cola
# =====================================================================
@dataclass(frozen=True)
class Proporcion:
    """Una proporción estimada por Monte Carlo y lo que la teoría normal promete."""

    aciertos: int
    B: int
    prometida: float

    @property
    def estimada(self) -> float:
        return self.aciertos / self.B

    @property
    def error_estandar(self) -> float:
        p = self.estimada
        return float(np.sqrt(p * (1 - p) / self.B))

    def intervalo(self) -> tuple[float, float]:
        e = 1.96 * self.error_estandar
        return max(0.0, self.estimada - e), min(1.0, self.estimada + e)

    def z(self) -> float:
        """Distancia a lo prometido, en errores estándar calculados como si la promesa fuera cierta."""
        p = self.prometida
        return float((self.estimada - p) / np.sqrt(p * (1 - p) / self.B))

    def compatible(self) -> bool:
        return abs(self.z()) <= 1.96


def cobertura(res: Resultado, alfa: float) -> Proporcion:
    """Fracción de réplicas en las que el IC de 8.125 contiene σ2²/σ1².

    Es lo mismo que la fracción de réplicas con F* dentro de [F_{1−α/2}, F_{α/2}].
    """
    a, b = fd.intervalo_central(alfa, res.escenario.n1, res.escenario.n2)
    F = res.F_pivote
    return Proporcion(int(((F >= a) & (F <= b)).sum()), len(F), 1 - alfa)


def cola_superior(res: Resultado, a: float) -> Proporcion:
    """Fracción de réplicas con F* > F_a (la F promete a)."""
    g1, g2 = res.escenario.gl
    c = fd.f_critico(a, g1, g2)
    return Proporcion(int((res.F_pivote > c).sum()), len(res.s2_1), a)


def cola_inferior(res: Resultado, a: float) -> Proporcion:
    """Fracción de réplicas con F* < F_{1−a} (la F promete a)."""
    g1, g2 = res.escenario.gl
    c = fd.f_critico(1 - a, g1, g2)
    return Proporcion(int((res.F_pivote < c).sum()), len(res.s2_1), a)


def _semilla(*partes: int) -> int:
    return int(np.random.SeedSequence([int(p) for p in partes]).generate_state(1)[0])


def barrido_n(f1: Forma, f2: Forma, ns: list[int], B: int, alfa: float, semilla: int,
              razon_n: float = 1.0, progreso: Progreso = None) -> pd.DataFrame:
    """Cobertura real del IC (o probabilidad central de F*) para varios n (n2 = round(razon_n · n1))."""
    filas = []
    for i, n in enumerate(ns):
        n2 = max(2, int(round(razon_n * n)))
        esc = Escenario(Poblacion(f1), Poblacion(f2), int(n), n2, B, _semilla(semilla, n, n2))
        sub = None if progreso is None else (lambda fr, i=i: progreso((i + fr) / len(ns)))
        res = simular(esc, sub)
        c = cobertura(res, alfa)
        filas.append({"n1": int(n), "n2": n2, "cobertura": c.estimada, "ee": c.error_estandar, "B": B,
                      "cola_sup": cola_superior(res, alfa / 2).estimada,
                      "cola_inf": cola_inferior(res, alfa / 2).estimada})
    return pd.DataFrame(filas)


def barrido_formas(formas: list[Forma], n: int, B: int, alfa: float, semilla: int,
                   progreso: Progreso = None) -> pd.DataFrame:
    """Cobertura real con la misma forma en las dos poblaciones, para un catálogo de formas."""
    filas = []
    for i, f in enumerate(formas):
        esc = Escenario(Poblacion(f), Poblacion(f), n, n, B, _semilla(semilla, i, n))
        sub = None if progreso is None else (lambda fr, i=i: progreso((i + fr) / len(formas)))
        res = simular(esc, sub)
        c = cobertura(res, alfa)
        filas.append({"forma": f.nombre_corto(), "clave": f.clave, "familia": f.espec.familia,
                      "curtosis": f.curtosis(), "asimetria": f.asimetria(),
                      "cobertura": c.estimada, "ee": c.error_estandar})
    return pd.DataFrame(filas)


def barrido_parejas(formas: list[Forma], n: int, B: int, alfa: float, semilla: int,
                    progreso: Progreso = None) -> pd.DataFrame:
    """Cobertura real para cada pareja (forma de la población 1, forma de la población 2)."""
    filas = []
    total = len(formas) ** 2
    k = 0
    for i, f1 in enumerate(formas):
        for j, f2 in enumerate(formas):
            esc = Escenario(Poblacion(f1), Poblacion(f2), n, n, B, _semilla(semilla, i, j, n))
            res = simular(esc)
            c = cobertura(res, alfa)
            filas.append({"pob1": f1.nombre_corto(), "pob2": f2.nombre_corto(), "cobertura": c.estimada,
                          "ee": c.error_estandar, "k1": f1.curtosis(), "k2": f2.curtosis()})
            k += 1
            if progreso is not None:
                progreso(k / total)
    return pd.DataFrame(filas)
