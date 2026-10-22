"""Distribuciones poblacionales del laboratorio.

Cada población declara su media, su varianza y su curtosis en exceso, y cómo
generar muestras aleatorias. Las fórmulas de media y varianza son las del libro:

- Normal:      Sección 4.5.
- Uniforme:    Sección 4.4.
- Exponencial: Sección 4.6 (caso gamma con alfa = 1); es la población de la Figura 7.5.
- Gamma:       Sección 4.6.
- Log-normal:  Ejercicios 4.182 y 4.183.
- t de Student como población de colas pesadas: Definición 7.2.
- Dado balanceado: Ejemplo 7.1.
- Bernoulli:   la variable X_i de la Sección 7.5 (suma de Bernoulli = binomial, Sección 3.4).

La curtosis en exceso NO aparece en los capítulos 7 y 8. Se usa solo en la
explicación complementaria del Experimento 6 (por qué el intervalo chi-cuadrado
para sigma^2 falla con poblaciones no normales) y se identifica como tal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class Parametro:
    """Especificación de un parámetro poblacional para la interfaz."""

    nombre: str          # nombre interno
    etiqueta: str        # etiqueta visible (puede llevar LaTeX en línea)
    defecto: float
    minimo: float
    maximo: float
    paso: float


@dataclass(frozen=True)
class EspecPoblacion:
    clave: str
    nombre: str
    referencia: str
    descripcion: str
    parametros: tuple[Parametro, ...]
    es_normal: bool = False
    es_bernoulli: bool = False
    es_exponencial: bool = False
    es_discreta: bool = False


ESPECIFICACIONES: dict[str, EspecPoblacion] = {
    "normal": EspecPoblacion(
        clave="normal",
        nombre="Normal",
        referencia="Sección 4.5",
        descripcion="La población que suponen los resultados exactos del capítulo 7.",
        parametros=(
            Parametro("mu", "Media μ", 0.0, -1000.0, 1000.0, 0.5),
            Parametro("sigma", "Desviación estándar σ", 1.0, 0.01, 1000.0, 0.1),
        ),
        es_normal=True,
    ),
    "uniforme": EspecPoblacion(
        clave="uniforme",
        nombre="Uniforme",
        referencia="Sección 4.4",
        descripcion="Simétrica, sin colas: el TCL actúa muy rápido.",
        parametros=(
            Parametro("a", "Extremo inferior a", 0.0, -1000.0, 1000.0, 0.5),
            Parametro("b", "Extremo superior b", 1.0, -1000.0, 1000.0, 0.5),
        ),
    ),
    "exponencial": EspecPoblacion(
        clave="exponencial",
        nombre="Exponencial",
        referencia="Sección 4.6; Figura 7.5 (θ = 10)",
        descripcion="Asimétrica a la derecha. Es la población del estudio de la Sección 7.3.",
        parametros=(Parametro("theta", "Media θ", 10.0, 0.01, 1000.0, 0.5),),
        es_exponencial=True,
    ),
    "gamma": EspecPoblacion(
        clave="gamma",
        nombre="Gamma",
        referencia="Sección 4.6",
        descripcion="Asimetría controlada por α: cuanto menor α, más asimétrica.",
        parametros=(
            Parametro("alpha", "Forma α", 2.0, 0.05, 100.0, 0.05),
            Parametro("beta", "Escala β", 1.0, 0.01, 1000.0, 0.1),
        ),
    ),
    "lognormal": EspecPoblacion(
        clave="lognormal",
        nombre="Log-normal",
        referencia="Ejercicios 4.182 y 4.183",
        descripcion="Cola derecha larga. ln(Y) es normal con media m y varianza s².",
        parametros=(
            Parametro("m", "Parámetro m", 0.0, -10.0, 10.0, 0.1),
            Parametro("s", "Parámetro s", 1.0, 0.05, 3.0, 0.05),
        ),
    ),
    "t": EspecPoblacion(
        clave="t",
        nombre="t de Student (colas pesadas)",
        referencia="Definición 7.2",
        descripcion="Simétrica con colas pesadas. Con ν ≤ 2 la varianza es infinita y el TCL no aplica.",
        parametros=(Parametro("nu", "Grados de libertad ν", 5.0, 1.5, 200.0, 0.5),),
    ),
    "dado": EspecPoblacion(
        clave="dado",
        nombre="Dado balanceado",
        referencia="Ejemplo 7.1",
        descripcion="Discreta, valores 1 a 6 con probabilidad 1/6.",
        parametros=(),
        es_discreta=True,
    ),
    "bernoulli": EspecPoblacion(
        clave="bernoulli",
        nombre="Bernoulli",
        referencia="Sección 7.5 (variables X_i); Sección 3.4",
        descripcion="Éxito (1) con probabilidad p. La suma de n ensayos es binomial.",
        parametros=(Parametro("p", "Probabilidad de éxito p", 0.5, 0.001, 0.999, 0.01),),
        es_bernoulli=True,
        es_discreta=True,
    ),
}


@dataclass(frozen=True)
class Poblacion:
    """Población concreta (especificación + valores de los parámetros).

    Es inmutable y comparable, de modo que puede usarse como clave de caché.
    """

    clave: str
    valores: tuple[tuple[str, float], ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------ básicos
    @property
    def espec(self) -> EspecPoblacion:
        return ESPECIFICACIONES[self.clave]

    @property
    def p(self) -> dict[str, float]:
        return dict(self.valores)

    @property
    def nombre(self) -> str:
        return self.espec.nombre

    def descripcion_corta(self) -> str:
        if not self.valores:
            return self.nombre
        partes = ", ".join(f"{k} = {_fmt(v)}" for k, v in self.valores)
        return f"{self.nombre} ({partes})"

    def validar(self) -> list[str]:
        """Devuelve la lista de errores de parámetros (vacía si todo está bien)."""
        errores: list[str] = []
        p = self.p
        for par in self.espec.parametros:
            if par.nombre not in p:
                errores.append(f"Falta el parámetro {par.etiqueta}.")
                continue
            v = p[par.nombre]
            if not np.isfinite(v):
                errores.append(f"{par.etiqueta} debe ser un número finito.")
        if self.clave == "normal" and p.get("sigma", 1) <= 0:
            errores.append("La desviación estándar σ debe ser positiva.")
        if self.clave == "uniforme" and not p.get("a", 0) < p.get("b", 1):
            errores.append("En la uniforme se necesita a < b.")
        if self.clave == "exponencial" and p.get("theta", 1) <= 0:
            errores.append("La media θ de la exponencial debe ser positiva.")
        if self.clave == "gamma" and (p.get("alpha", 1) <= 0 or p.get("beta", 1) <= 0):
            errores.append("En la gamma, α y β deben ser positivos.")
        if self.clave == "lognormal" and p.get("s", 1) <= 0:
            errores.append("En la log-normal, s debe ser positivo.")
        if self.clave == "t" and p.get("nu", 5) <= 1:
            errores.append("La población t necesita ν > 1 para que exista la media.")
        if self.clave == "bernoulli" and not 0 < p.get("p", 0.5) < 1:
            errores.append("La probabilidad p debe estar estrictamente entre 0 y 1.")
        return errores

    # ------------------------------------------------------------- momentos
    def media(self) -> float:
        p = self.p
        c = self.clave
        if c == "normal":
            return p["mu"]
        if c == "uniforme":
            return (p["a"] + p["b"]) / 2
        if c == "exponencial":
            return p["theta"]
        if c == "gamma":
            return p["alpha"] * p["beta"]
        if c == "lognormal":
            return float(np.exp(p["m"] + p["s"] ** 2 / 2))
        if c == "t":
            return 0.0
        if c == "dado":
            return 3.5
        if c == "bernoulli":
            return p["p"]
        raise KeyError(c)

    def varianza(self) -> float:
        """Varianza poblacional; ``inf`` si no es finita."""
        p = self.p
        c = self.clave
        if c == "normal":
            return p["sigma"] ** 2
        if c == "uniforme":
            return (p["b"] - p["a"]) ** 2 / 12
        if c == "exponencial":
            return p["theta"] ** 2
        if c == "gamma":
            return p["alpha"] * p["beta"] ** 2
        if c == "lognormal":
            s2 = p["s"] ** 2
            return float(np.exp(2 * p["m"] + s2) * (np.exp(s2) - 1))
        if c == "t":
            nu = p["nu"]
            return nu / (nu - 2) if nu > 2 else float("inf")
        if c == "dado":
            return 35 / 12
        if c == "bernoulli":
            return p["p"] * (1 - p["p"])
        raise KeyError(c)

    def desviacion(self) -> float:
        return float(np.sqrt(self.varianza()))

    def varianza_finita(self) -> bool:
        return bool(np.isfinite(self.varianza()))

    def curtosis_exceso(self) -> float:
        """Curtosis en exceso, E[(Y-mu)^4]/sigma^4 - 3. (Complementario, no del libro.)"""
        p = self.p
        c = self.clave
        if c == "normal":
            return 0.0
        if c == "uniforme":
            return -1.2
        if c == "exponencial":
            return 6.0
        if c == "gamma":
            return 6.0 / p["alpha"]
        if c == "lognormal":
            s2 = p["s"] ** 2
            return float(np.exp(4 * s2) + 2 * np.exp(3 * s2) + 3 * np.exp(2 * s2) - 6)
        if c == "t":
            nu = p["nu"]
            return 6.0 / (nu - 4) if nu > 4 else float("inf")
        if c == "dado":
            k = 6
            return -6 * (k**2 + 1) / (5 * (k**2 - 1))
        if c == "bernoulli":
            q = p["p"]
            return (1 - 6 * q * (1 - q)) / (q * (1 - q))
        raise KeyError(c)

    # ------------------------------------------------------------- muestreo
    def muestrear(self, rng: np.random.Generator, forma: tuple[int, ...]) -> np.ndarray:
        """Genera una matriz de observaciones i.i.d. con la forma pedida."""
        p = self.p
        c = self.clave
        if c == "normal":
            return rng.normal(p["mu"], p["sigma"], size=forma)
        if c == "uniforme":
            return rng.uniform(p["a"], p["b"], size=forma)
        if c == "exponencial":
            return rng.exponential(p["theta"], size=forma)
        if c == "gamma":
            return rng.gamma(p["alpha"], p["beta"], size=forma)
        if c == "lognormal":
            return rng.lognormal(p["m"], p["s"], size=forma)
        if c == "t":
            return rng.standard_t(p["nu"], size=forma)
        if c == "dado":
            return rng.integers(1, 7, size=forma).astype(np.float64)
        if c == "bernoulli":
            return (rng.random(size=forma) < p["p"]).astype(np.float64)
        raise KeyError(c)

    # ------------------------------------------------------------- densidad
    def densidad(self) -> Callable[[np.ndarray], np.ndarray] | None:
        """Función de densidad (o de probabilidad) para graficar la población."""
        p = self.p
        c = self.clave
        if c == "normal":
            return stats.norm(p["mu"], p["sigma"]).pdf
        if c == "uniforme":
            return stats.uniform(p["a"], p["b"] - p["a"]).pdf
        if c == "exponencial":
            return stats.expon(scale=p["theta"]).pdf
        if c == "gamma":
            return stats.gamma(p["alpha"], scale=p["beta"]).pdf
        if c == "lognormal":
            return stats.lognorm(p["s"], scale=np.exp(p["m"])).pdf
        if c == "t":
            return stats.t(p["nu"]).pdf
        return None

    def rango_grafico(self) -> tuple[float, float]:
        p = self.p
        c = self.clave
        if c == "normal":
            return p["mu"] - 4 * p["sigma"], p["mu"] + 4 * p["sigma"]
        if c == "uniforme":
            ancho = p["b"] - p["a"]
            return p["a"] - 0.15 * ancho, p["b"] + 0.15 * ancho
        if c == "exponencial":
            return 0.0, stats.expon(scale=p["theta"]).ppf(0.995)
        if c == "gamma":
            return 0.0, stats.gamma(p["alpha"], scale=p["beta"]).ppf(0.995)
        if c == "lognormal":
            return 0.0, stats.lognorm(p["s"], scale=np.exp(p["m"])).ppf(0.98)
        if c == "t":
            return -6.0, 6.0
        if c == "dado":
            return 0.5, 6.5
        return -0.5, 1.5


def _fmt(v: float) -> str:
    if float(v).is_integer():
        return f"{int(v)}"
    return f"{v:g}"


def crear(clave: str, **valores: float) -> Poblacion:
    """Crea una población completando con los valores por defecto."""
    espec = ESPECIFICACIONES[clave]
    completos = {par.nombre: float(par.defecto) for par in espec.parametros}
    completos.update({k: float(v) for k, v in valores.items()})
    orden = tuple((par.nombre, completos[par.nombre]) for par in espec.parametros)
    return Poblacion(clave, orden)


#: Poblaciones admitidas para procedimientos de una muestra sobre la media/varianza.
CONTINUAS_O_MEDIA = ("normal", "uniforme", "exponencial", "gamma", "lognormal", "t", "dado")
