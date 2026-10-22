"""Motor de simulación de Monte Carlo.

Conceptos que el motor distingue rigurosamente
-----------------------------------------------
- ``n``: tamaño de CADA muestra (número de observaciones Y₁, …, Yₙ).
- ``B``: número de muestras independientes (réplicas del experimento).

"Una muestra de 100 000 observaciones" es n = 100 000 y B = 1: produce UN
intervalo. "100 000 muestras" es B = 100 000: produce cien mil intervalos, y
con ellos se estima la cobertura. El costo es proporcional a n × B.

Administración de memoria
-------------------------
Las observaciones nunca se guardan todas a la vez. Se generan por lotes de a lo
sumo ``MAX_ELEMENTOS_LOTE`` números (≈ 32 MB en float64) y de cada lote solo se
conservan los estadísticos suficientes que necesitan los intervalos: media,
varianza muestral (con divisor n − 1) y suma. Así, 1000 muestras de tamaño
100 000 (10⁸ observaciones, que serían 800 MB) se procesan con memoria acotada.

Reproducibilidad
----------------
Cada simulación usa ``numpy.random.default_rng(semilla)``. Con la misma semilla
y los mismos parámetros se obtienen exactamente los mismos números. En el caso
de dos muestras, cada población usa su propio generador hijo de la misma semilla
(``SeedSequence.spawn``), de modo que las muestras son independientes.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from . import intervalos as ic
from .poblaciones import Poblacion
from .procedimientos import (
    DOS_MUESTRAS,
    DOS_PROPORCIONES,
    PROCEDIMIENTOS,
    PROPORCION,
    UNA_MUESTRA,
    Procedimiento,
)

MAX_ELEMENTOS_LOTE = 4_000_000        # números por lote (≈ 32 MB en float64)
LIMITE_OBSERVACIONES = 300_000_000    # tope de n × B por simulación
N_MAXIMO = 100_000
B_MAXIMO = 200_000

Progreso = Callable[[float], None] | None


class ErrorSimulacion(ValueError):
    """Parámetros inválidos o fuera de los límites computacionales."""


# =====================================================================
# Escenario
# =====================================================================
@dataclass(frozen=True)
class Escenario:
    procedimiento: str
    pob1: Poblacion
    n1: int
    B: int
    alfa: float = 0.05
    lado: str = "bilateral"
    semilla: int = 12345
    pob2: Poblacion | None = None
    n2: int | None = None

    @property
    def proc(self) -> Procedimiento:
        return PROCEDIMIENTOS[self.procedimiento]

    @property
    def dos_muestras(self) -> bool:
        return self.proc.familia in (DOS_MUESTRAS, DOS_PROPORCIONES)

    def observaciones_totales(self) -> int:
        """Número de variables aleatorias que hay que generar (n × B)."""
        f = self.proc.familia
        if f == PROPORCION:
            return self.B  # se genera directamente Y ~ Binomial(n, p): un número por réplica
        if f == DOS_PROPORCIONES:
            return 2 * self.B
        total = self.n1 * self.B
        if self.dos_muestras:
            total += (self.n2 or 0) * self.B
        return total

    def parametro_verdadero(self) -> float:
        return float(self.proc.verdadero(self.pob1, self.pob2))

    def validar(self) -> None:
        errores = validar_escenario(self)
        if errores:
            raise ErrorSimulacion(" ".join(errores))


def validar_escenario(e: Escenario) -> list[str]:
    errores: list[str] = []
    if e.procedimiento not in PROCEDIMIENTOS:
        return [f"Procedimiento desconocido: {e.procedimiento}."]
    proc = e.proc
    errores += e.pob1.validar()
    if e.pob1.clave not in proc.poblaciones:
        errores.append(f"«{proc.nombre}» no está definido para la población {e.pob1.nombre}.")
    if not (0 < e.alfa < 1):
        errores.append("El nivel de confianza debe estar estrictamente entre 0 % y 100 %.")
    if e.lado not in ic.LADOS:
        errores.append("Tipo de intervalo desconocido.")
    minimo_n = 1 if proc.clave in ("media_z_sigma", "exponencial_chi2", "proporcion_wald", "dif_proporciones") else 2
    if int(e.n1) != e.n1 or e.n1 < minimo_n:
        errores.append(f"El tamaño muestral n debe ser un entero ≥ {minimo_n}.")
    if e.n1 > N_MAXIMO:
        errores.append(f"El tamaño muestral máximo es n = {N_MAXIMO:,}.".replace(",", "."))
    if int(e.B) != e.B or e.B < 1:
        errores.append("El número de simulaciones B debe ser un entero ≥ 1.")
    if e.B > B_MAXIMO:
        errores.append(f"El número máximo de simulaciones es B = {B_MAXIMO:,}.".replace(",", "."))
    if e.dos_muestras:
        if e.pob2 is None or e.n2 is None:
            errores.append("Este procedimiento necesita dos poblaciones y dos tamaños muestrales.")
        else:
            errores += [f"Población 2: {m}" for m in e.pob2.validar()]
            if e.pob2.clave not in proc.poblaciones:
                errores.append(f"«{proc.nombre}» no está definido para la población {e.pob2.nombre}.")
            if int(e.n2) != e.n2 or e.n2 < minimo_n:
                errores.append(f"El tamaño muestral n₂ debe ser un entero ≥ {minimo_n}.")
            if e.n2 > N_MAXIMO:
                errores.append(f"El tamaño máximo es n₂ = {N_MAXIMO:,}.".replace(",", "."))
    if proc.clave == "media_z_sigma" and not e.pob1.varianza_finita():
        errores.append("El intervalo Z con σ conocida exige σ² < ∞, y esta población tiene varianza infinita.")
    if proc.clave in ("varianza_chi2", "razon_varianzas_f") and not e.pob1.varianza_finita():
        errores.append("El parámetro σ² no existe (es infinito) para esta población.")
    if not errores and e.observaciones_totales() > LIMITE_OBSERVACIONES:
        errores.append(
            f"La simulación pediría generar {e.observaciones_totales():,} observaciones (n × B). "
            f"El límite es {LIMITE_OBSERVACIONES:,}. Reduzca n o B.".replace(",", ".")
        )
    return errores


# =====================================================================
# Generación de estadísticos por lotes
# =====================================================================
def filas_por_lote(n: int, B: int) -> int:
    return int(max(1, min(B, MAX_ELEMENTOS_LOTE // max(n, 1))))


def estadisticos_una_muestra(
    pob: Poblacion, n: int, B: int, rng: np.random.Generator, progreso: Progreso = None,
    peso_progreso: tuple[float, float] = (0.0, 1.0),
) -> dict[str, np.ndarray]:
    """Media, varianza muestral S² (divisor n − 1) y suma de B muestras de tamaño n."""
    media = np.empty(B)
    var = np.empty(B)
    suma = np.empty(B)
    filas = filas_por_lote(n, B)
    inicio = 0
    a, b = peso_progreso
    while inicio < B:
        fin = min(B, inicio + filas)
        X = pob.muestrear(rng, (fin - inicio, n))
        s = X.sum(axis=1)
        suma[inicio:fin] = s
        media[inicio:fin] = s / n
        if n > 1:
            var[inicio:fin] = X.var(axis=1, ddof=1)
        else:
            var[inicio:fin] = np.nan
        del X
        inicio = fin
        if progreso is not None:
            progreso(a + (b - a) * inicio / B)
    return {"media": media, "var": var, "suma": suma, "n": n}


def estadisticos_proporcion(pob: Poblacion, n: int, B: int, rng: np.random.Generator) -> dict:
    """Número de éxitos Y = ΣXᵢ de B experimentos binomiales.

    Se genera Y ~ Binomial(n, p) directamente: es exactamente la distribución de la
    suma de n variables de Bernoulli independientes (Sección 7.5), de modo que el
    resultado es idéntico en distribución y el costo no depende de n.
    """
    exitos = rng.binomial(n, pob.p["p"], size=B).astype(float)
    return {"exitos": exitos, "n": n}


def _generadores(semilla: int, k: int) -> list[np.random.Generator]:
    return [np.random.default_rng(s) for s in np.random.SeedSequence(semilla).spawn(k)]


def generar_estadisticos(esc: Escenario, progreso: Progreso = None) -> dict:
    """Genera los estadísticos de las B réplicas del escenario."""
    esc.validar()
    f = esc.proc.familia
    if f == UNA_MUESTRA:
        rng = np.random.default_rng(esc.semilla)
        return estadisticos_una_muestra(esc.pob1, esc.n1, esc.B, rng, progreso)
    if f == PROPORCION:
        rng = np.random.default_rng(esc.semilla)
        out = estadisticos_proporcion(esc.pob1, esc.n1, esc.B, rng)
        if progreso:
            progreso(1.0)
        return out
    r1, r2 = _generadores(esc.semilla, 2)
    if f == DOS_PROPORCIONES:
        a = estadisticos_proporcion(esc.pob1, esc.n1, esc.B, r1)
        b = estadisticos_proporcion(esc.pob2, esc.n2, esc.B, r2)
        if progreso:
            progreso(1.0)
        return {"exitos1": a["exitos"], "n1": esc.n1, "exitos2": b["exitos"], "n2": esc.n2}
    # dos muestras continuas
    c1 = esc.n1 / (esc.n1 + esc.n2)
    a = estadisticos_una_muestra(esc.pob1, esc.n1, esc.B, r1, progreso, (0.0, c1))
    b = estadisticos_una_muestra(esc.pob2, esc.n2, esc.B, r2, progreso, (c1, 1.0))
    return {
        "media1": a["media"], "var1": a["var"], "n1": esc.n1,
        "media2": b["media"], "var2": b["var"], "n2": esc.n2,
    }


# =====================================================================
# Resultados
# =====================================================================
@dataclass
class Resultado:
    escenario: Escenario
    tabla: pd.DataFrame            # una fila por réplica
    theta: float                   # parámetro verdadero
    segundos: float
    estadisticos: dict = field(repr=False, default_factory=dict)

    @property
    def B(self) -> int:
        return len(self.tabla)

    def cobertura(self) -> "Cobertura":
        return resumen_cobertura(self.tabla["cubre"].to_numpy(), 1 - self.escenario.alfa)


@dataclass(frozen=True)
class Cobertura:
    """Estimación Monte Carlo de la cobertura.

    La cobertura empírica ĉ = (número de intervalos que contienen θ)/B es una
    proporción muestral de B ensayos de Bernoulli independientes con probabilidad
    c (la cobertura real). Por la Tabla 8.1 su error estándar es √(c(1 − c)/B), que
    se estima con ĉ. Su intervalo del 95 % es el de la Sección 8.6.
    """

    estimada: float
    nominal: float
    B: int
    aciertos: int

    @property
    def error_estandar(self) -> float:
        c = self.estimada
        return float(np.sqrt(c * (1 - c) / self.B))

    @property
    def error_estandar_nominal(self) -> float:
        """Error estándar si la cobertura real fuera exactamente la nominal."""
        c = self.nominal
        return float(np.sqrt(c * (1 - c) / self.B))

    def intervalo(self, alfa: float = 0.05) -> tuple[float, float]:
        z = ic.z_critico(alfa / 2)
        return self.estimada - z * self.error_estandar, self.estimada + z * self.error_estandar

    def z_desviacion(self) -> float:
        """Distancia (en errores estándar bajo la cobertura nominal) entre ĉ y 1 − α."""
        ee = self.error_estandar_nominal
        return float((self.estimada - self.nominal) / ee) if ee > 0 else float("nan")

    def compatible_con_nominal(self, alfa: float = 0.05) -> bool:
        return abs(self.z_desviacion()) <= ic.z_critico(alfa / 2)


def resumen_cobertura(cubre: np.ndarray, nominal: float) -> Cobertura:
    cubre = np.asarray(cubre, dtype=bool)
    B = int(cubre.size)
    if B == 0:
        raise ErrorSimulacion("No hay réplicas para estimar la cobertura.")
    k = int(cubre.sum())
    return Cobertura(estimada=k / B, nominal=nominal, B=B, aciertos=k)


def calcular_intervalos(esc: Escenario, est: dict, alfa: float | None = None, lado: str | None = None,
                        procedimiento: str | None = None) -> pd.DataFrame:
    """Aplica la fórmula del procedimiento a los estadísticos ya generados.

    Permite reutilizar las MISMAS muestras con otro nivel de confianza, otro tipo
    de intervalo u otro procedimiento compatible (Experimentos 3 y 4).
    """
    alfa = esc.alfa if alfa is None else alfa
    lado = esc.lado if lado is None else lado
    proc = PROCEDIMIENTOS[procedimiento or esc.procedimiento]
    theta = float(proc.verdadero(esc.pob1, esc.pob2))
    with np.errstate(invalid="ignore", divide="ignore"):
        estimador, L, U = proc.calcular(est, alfa, lado, esc.pob1, esc.pob2)
    estimador = np.broadcast_to(np.asarray(estimador, dtype=float), np.shape(L))
    tabla = pd.DataFrame({
        "replica": np.arange(1, len(L) + 1),
        "estimador": estimador,
        "L": L,
        "U": U,
    })
    tabla["cubre"] = ic.contiene(tabla["L"], tabla["U"], theta)
    tabla["amplitud"] = tabla["U"] - tabla["L"]
    return tabla


def simular(esc: Escenario, progreso: Progreso = None) -> Resultado:
    """Ejecuta el experimento completo: B muestras → B intervalos."""
    t0 = time.perf_counter()
    est = generar_estadisticos(esc, progreso)
    tabla = calcular_intervalos(esc, est)
    return Resultado(
        escenario=esc,
        tabla=tabla,
        theta=esc.parametro_verdadero(),
        segundos=time.perf_counter() - t0,
        estadisticos=est,
    )


# =====================================================================
# Recuperar una muestra individual (para inspeccionarla)
# =====================================================================
def muestra_individual(esc: Escenario, replica: int) -> dict[str, np.ndarray]:
    """Regenera exactamente las observaciones de la réplica ``replica`` (1, …, B).

    Se repite la misma secuencia de lotes que en la simulación original, de modo
    que los números coinciden con los usados para construir el intervalo.
    """
    if not 1 <= replica <= esc.B:
        raise ErrorSimulacion(f"La réplica debe estar entre 1 y {esc.B}.")
    f = esc.proc.familia
    k = replica - 1
    if f == UNA_MUESTRA:
        return {"y1": _fila(esc.pob1, esc.n1, esc.B, np.random.default_rng(esc.semilla), k)}
    if f in (DOS_MUESTRAS,):
        r1, r2 = _generadores(esc.semilla, 2)
        return {
            "y1": _fila(esc.pob1, esc.n1, esc.B, r1, k),
            "y2": _fila(esc.pob2, esc.n2, esc.B, r2, k),
        }
    # Proporciones: solo se generó el conteo Y ~ Binomial; no hay secuencia 0/1 que mostrar.
    return {}


def _fila(pob: Poblacion, n: int, B: int, rng: np.random.Generator, k: int) -> np.ndarray:
    filas = filas_por_lote(n, B)
    inicio = 0
    while inicio < B:
        fin = min(B, inicio + filas)
        X = pob.muestrear(rng, (fin - inicio, n))
        if inicio <= k < fin:
            return X[k - inicio].copy()
        inicio = fin
    raise ErrorSimulacion("Réplica fuera de rango.")


# =====================================================================
# Una sola muestra que crece (Experimento 2, segunda vista)
# =====================================================================
def trayectoria_una_muestra(
    procedimiento: str, pob: Poblacion, n_max: int, alfa: float, semilla: int, puntos: int = 120,
) -> pd.DataFrame:
    """Genera UNA muestra de tamaño ``n_max`` y calcula el intervalo con sus primeras k observaciones.

    Sirve para contrastar "una muestra de 100 000 observaciones" (un intervalo cada
    vez más estrecho alrededor de θ) con "muchas muestras" (cobertura).
    """
    proc = PROCEDIMIENTOS[procedimiento]
    if proc.familia not in (UNA_MUESTRA, PROPORCION):
        raise ErrorSimulacion("La trayectoria solo está disponible para procedimientos de una muestra.")
    if not 2 <= n_max <= N_MAXIMO:
        raise ErrorSimulacion(f"El tamaño máximo debe estar entre 2 y {N_MAXIMO}.")
    rng = np.random.default_rng(semilla)
    x = pob.muestrear(rng, (n_max,))
    ks = np.unique(np.geomspace(2, n_max, puntos).astype(int))
    # Sumas acumuladas centradas en x[0] para estabilidad numérica.
    c = x - x[0]
    s1 = np.cumsum(c)
    s2 = np.cumsum(c * c)
    k = ks.astype(float)
    media = x[0] + s1[ks - 1] / k
    var = (s2[ks - 1] - s1[ks - 1] ** 2 / k) / (k - 1)
    var = np.maximum(var, 0.0)
    suma = media * k
    if proc.familia == PROPORCION:
        est = {"exitos": suma, "n": ks}
    else:
        est = {"media": media, "var": var, "suma": suma, "n": ks}
    filas = []
    for i, kk in enumerate(ks):
        e_i = {key: (val[i] if isinstance(val, np.ndarray) else val) for key, val in est.items()}
        e_i["n"] = int(kk)
        estim, L, U = proc.calcular(e_i, alfa, "bilateral", pob, None)
        filas.append((int(kk), float(estim), float(L), float(U)))
    df = pd.DataFrame(filas, columns=["n", "estimador", "L", "U"])
    theta = float(proc.verdadero(pob, None))
    df["amplitud"] = df["U"] - df["L"]
    df["cubre"] = ic.contiene(df["L"], df["U"], theta)
    return df


# =====================================================================
# Barrido en n (Experimentos 2, 3 y 6)
# =====================================================================
def barrido_n(
    esc_base: Escenario, ns: list[int], progreso: Progreso = None, procedimientos: list[str] | None = None,
    ns2: list[int] | None = None,
) -> pd.DataFrame:
    """Para cada n de la lista, simula B réplicas y resume amplitud y cobertura.

    Cada n usa una semilla derivada ``[semilla, n]``, de modo que el barrido es
    reproducible y los distintos n son independientes entre sí. Si se pasan varios
    procedimientos compatibles, todos se evalúan sobre LAS MISMAS muestras.
    """
    procs = procedimientos or [esc_base.procedimiento]
    filas = []
    total = len(ns)
    for i, n in enumerate(ns):
        n2 = (ns2[i] if ns2 is not None else (esc_base.n2 and n)) if esc_base.dos_muestras else None
        esc = Escenario(
            procedimiento=esc_base.procedimiento, pob1=esc_base.pob1, n1=int(n), B=esc_base.B,
            alfa=esc_base.alfa, lado=esc_base.lado, semilla=_semilla_derivada(esc_base.semilla, int(n)),
            pob2=esc_base.pob2, n2=None if n2 is None else int(n2),
        )
        sub = None
        if progreso is not None:
            a, b = i / total, (i + 1) / total
            sub = (lambda fr, a=a, b=b: progreso(a + (b - a) * fr))
        est = generar_estadisticos(esc, sub)
        for clave in procs:
            tabla = calcular_intervalos(esc, est, procedimiento=clave)
            cob = resumen_cobertura(tabla["cubre"].to_numpy(), 1 - esc.alfa)
            amp = tabla["amplitud"].to_numpy()
            finitos = np.isfinite(amp)
            filas.append({
                "procedimiento": clave,
                "n": int(n),
                "n2": n2,
                "B": esc.B,
                "cobertura": cob.estimada,
                "ee_cobertura": cob.error_estandar,
                "amplitud_media": float(np.mean(amp[finitos])) if finitos.any() else np.nan,
                "amplitud_de": float(np.std(amp[finitos], ddof=1)) if finitos.sum() > 1 else np.nan,
                "estimador_media": float(np.mean(tabla["estimador"])),
                "estimador_de": float(np.std(tabla["estimador"], ddof=1)) if len(tabla) > 1 else np.nan,
            })
    if progreso is not None:
        progreso(1.0)
    return pd.DataFrame(filas)


def _semilla_derivada(semilla: int, n: int) -> int:
    return int(np.random.SeedSequence([semilla, n]).generate_state(1)[0])


def memoria_estimada_mb(n: int, B: int) -> float:
    """Memoria máxima aproximada de un lote, en MB."""
    return filas_por_lote(n, B) * n * 8 / 1e6
