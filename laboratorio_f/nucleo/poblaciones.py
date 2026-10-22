"""Formas poblacionales para estudiar la distribución F.

Idea clave del diseño
---------------------
El estadístico F = S1²/S2² no cambia si a una muestra se le suma una constante
(S² no depende de la media), y tampoco cambia la *forma* de su distribución si
se multiplican ambas poblaciones por la misma constante. Por eso cada población
se describe con:

* una **forma** estandarizada X con E(X) = 0 y V(X) = 1 (normal, uniforme,
  t de Student, exponencial, gamma, log-normal), y
* una **escala** σ y una **posición** μ:  Y = μ + σ·X.

Así, V(Y) = σ² exactamente para todas las formas, y con σ1 = σ2 lo único
que distingue un escenario de otro es la forma, es decir, la asimetría y la
curtosis (las colas).

Referencias para medias y varianzas: Secciones 4.4 (uniforme), 4.5 (normal),
4.6 (gamma, exponencial), Ejercicios 4.182–4.183 (log-normal) y Definición 7.2
(t de Student). La curtosis y la asimetría no se tratan en los capítulos 7 y 8;
se usan como herramientas complementarias y la interfaz lo indica.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class EspecForma:
    clave: str
    nombre: str
    familia: str            # "normal" | "colas livianas" | "colas pesadas" | "asimétrica"
    referencia: str
    descripcion: str
    parametro: str | None   # nombre del parámetro de forma
    etiqueta: str | None
    defecto: float | None
    minimo: float | None
    maximo: float | None
    paso: float | None


FORMAS: dict[str, EspecForma] = {
    "normal": EspecForma("normal", "Normal", "normal", "Sección 4.5",
                         "La única forma para la que el Teorema 7.3 y la Definición 7.3 dan una F exacta.",
                         None, None, None, None, None, None),
    "uniforme": EspecForma("uniforme", "Uniforme", "colas livianas", "Sección 4.4",
                           "Simétrica y sin colas: curtosis negativa (−1.2).",
                           None, None, None, None, None, None),
    "t": EspecForma("t", "t de Student", "colas pesadas", "Definición 7.2",
                    "Simétrica con colas pesadas. Cuanto menor ν, más pesadas; con ν ≤ 4 la curtosis es infinita.",
                    "nu", "Grados de libertad ν", 5.0, 2.5, 100.0, 0.5),
    "exponencial": EspecForma("exponencial", "Exponencial", "asimétrica", "Sección 4.6",
                              "Asimétrica a la derecha (asimetría 2, curtosis 6).",
                              None, None, None, None, None, None),
    "gamma": EspecForma("gamma", "Gamma", "asimétrica", "Sección 4.6",
                        "Asimetría 2/√α y curtosis 6/α: con α grande se parece a la normal.",
                        "alpha", "Forma α", 2.0, 0.2, 100.0, 0.1),
    "lognormal": EspecForma("lognormal", "Log-normal", "asimétrica", "Ejercicios 4.182 y 4.183",
                            "Muy asimétrica, con cola derecha larga; la curtosis crece muy rápido con s.",
                            "s", "Parámetro s", 0.5, 0.05, 1.5, 0.05),
}


@dataclass(frozen=True)
class Forma:
    """Forma estandarizada: E(X) = 0, V(X) = 1."""

    clave: str
    valor: float | None = None   # parámetro de forma (ν, α o s) si aplica

    @property
    def espec(self) -> EspecForma:
        return FORMAS[self.clave]

    @property
    def es_normal(self) -> bool:
        return self.clave == "normal"

    def nombre_corto(self) -> str:
        e = self.espec
        if e.parametro is None:
            return e.nombre
        simbolo = {"nu": "ν", "alpha": "α", "s": "s"}[e.parametro]
        return f"{e.nombre} ({simbolo} = {self.valor:g})"

    def validar(self) -> list[str]:
        e = self.espec
        if e.parametro is None:
            return []
        v = self.valor
        if v is None or not np.isfinite(v):
            return [f"Falta el parámetro de forma de la {e.nombre.lower()}."]
        if self.clave == "t" and v <= 2:
            return ["La t de Student necesita ν > 2 para tener varianza finita."]
        if v <= 0:
            return [f"El parámetro de forma de la {e.nombre.lower()} debe ser positivo."]
        return []

    # ------------------------------------------------------------ momentos
    def curtosis(self) -> float:
        """Curtosis en exceso κ = E(X⁴) − 3 (complementario)."""
        c, v = self.clave, self.valor
        if c == "normal":
            return 0.0
        if c == "uniforme":
            return -1.2
        if c == "t":
            return 6.0 / (v - 4) if v > 4 else float("inf")
        if c == "exponencial":
            return 6.0
        if c == "gamma":
            return 6.0 / v
        if c == "lognormal":
            s2 = v * v
            return float(np.exp(4 * s2) + 2 * np.exp(3 * s2) + 3 * np.exp(2 * s2) - 6)
        raise KeyError(c)

    def asimetria(self) -> float:
        """Coeficiente de asimetría E(X³) (complementario)."""
        c, v = self.clave, self.valor
        if c in ("normal", "uniforme", "t"):
            return 0.0
        if c == "exponencial":
            return 2.0
        if c == "gamma":
            return 2.0 / np.sqrt(v)
        if c == "lognormal":
            s2 = v * v
            return float((np.exp(s2) + 2) * np.sqrt(np.exp(s2) - 1))
        raise KeyError(c)

    # ------------------------------------------------------------ muestreo
    def muestrear(self, rng: np.random.Generator, forma: tuple[int, ...]) -> np.ndarray:
        c, v = self.clave, self.valor
        if c == "normal":
            return rng.standard_normal(forma)
        if c == "uniforme":
            return rng.uniform(-np.sqrt(3.0), np.sqrt(3.0), forma)
        if c == "t":
            return rng.standard_t(v, forma) * np.sqrt((v - 2) / v)
        if c == "exponencial":
            return rng.standard_exponential(forma) - 1.0
        if c == "gamma":
            return (rng.standard_gamma(v, forma) - v) / np.sqrt(v)
        if c == "lognormal":
            m = np.exp(v * v / 2)
            d = np.sqrt((np.exp(v * v) - 1) * np.exp(v * v))
            return (np.exp(v * rng.standard_normal(forma)) - m) / d
        raise KeyError(c)

    # ------------------------------------------------------------ densidad
    def densidad(self) -> Callable[[np.ndarray], np.ndarray]:
        """Densidad de la forma estandarizada X."""
        c, v = self.clave, self.valor
        if c == "normal":
            return stats.norm.pdf
        if c == "uniforme":
            return stats.uniform(-np.sqrt(3), 2 * np.sqrt(3)).pdf
        if c == "t":
            k = np.sqrt((v - 2) / v)
            return lambda x: stats.t.pdf(x / k, v) / k
        if c == "exponencial":
            return stats.expon(loc=-1).pdf
        if c == "gamma":
            return lambda x: stats.gamma.pdf(x * np.sqrt(v) + v, v) * np.sqrt(v)
        if c == "lognormal":
            m = np.exp(v * v / 2)
            d = np.sqrt((np.exp(v * v) - 1) * np.exp(v * v))
            return lambda x: stats.lognorm.pdf(x * d + m, v) * d
        raise KeyError(c)


@dataclass(frozen=True)
class Poblacion:
    """Y = μ + σ·X, con X de la forma indicada. E(Y) = μ, V(Y) = σ²."""

    forma: Forma
    sigma: float = 1.0
    mu: float = 0.0

    def validar(self) -> list[str]:
        errores = self.forma.validar()
        if not (self.sigma > 0 and np.isfinite(self.sigma)):
            errores.append("La desviación estándar σ debe ser positiva.")
        if not np.isfinite(self.mu):
            errores.append("La media μ debe ser un número finito.")
        return errores

    @property
    def varianza(self) -> float:
        return self.sigma ** 2

    def muestrear(self, rng: np.random.Generator, forma: tuple[int, ...]) -> np.ndarray:
        return self.mu + self.sigma * self.forma.muestrear(rng, forma)

    def descripcion(self) -> str:
        return f"{self.forma.nombre_corto()}, μ = {self.mu:g}, σ = {self.sigma:g}"


def forma(clave: str, valor: float | None = None) -> Forma:
    e = FORMAS[clave]
    if e.parametro is not None and valor is None:
        valor = e.defecto
    return Forma(clave, None if e.parametro is None else float(valor))


#: Catálogo para el mapa de robustez: formas con curtosis finita y variada.
CATALOGO_ROBUSTEZ: list[Forma] = [
    forma("uniforme"),
    forma("normal"),
    forma("gamma", 16.0),
    forma("t", 16.0),
    forma("gamma", 6.0),
    forma("t", 10.0),
    forma("gamma", 3.0),
    forma("t", 7.0),
    forma("lognormal", 0.3),
    forma("gamma", 1.5),
    forma("exponencial"),
    forma("t", 5.5),
    forma("gamma", 0.75),
    forma("lognormal", 0.5),
]
