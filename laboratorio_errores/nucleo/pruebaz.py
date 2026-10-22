"""Prueba Z para una media con σ conocida (Secciones 10.2 y 10.4).

Supuestos: Y1, …, Yn muestra aleatoria de una población normal con media μ y desviación
estándar σ CONOCIDA. Entonces la media muestral Ȳ ~ Normal(μ, σ/√n) exactamente.

Notación
--------
μ0       media bajo H0.
μ1       un valor ESPECÍFICO de μ dentro de Ha.
σ        desviación estándar poblacional (conocida).
n        tamaño de muestra.
EE       error estándar de Ȳ: σ/√n.
α        nivel de significancia.
z_α      cuantil con área α a la derecha: P(Z > z_α) = α.
k        frontera de la región de rechazo, en la escala de Ȳ.
cola     "superior": H0: μ = μ0, Ha: μ > μ0, RR = {ȳ > k},  k = μ0 + z_α·EE
         "inferior": H0: μ = μ0, Ha: μ < μ0, RR = {ȳ < k},  k = μ0 − z_α·EE

Probabilidades de error en función de la frontera k (cola superior)
    α(k) = P(Ȳ > k | μ0) = 1 − Φ((k − μ0)/EE)     disminuye cuando k aumenta
    β(k) = P(Ȳ ≤ k | μ1) = Φ((k − μ1)/EE)         aumenta cuando k aumenta
Ese par de monotonías es el «dilema» entre α y β.

Tamaño muestral para α y β dados (Sección 10.4):
    n = (z_α + z_β)² σ² / (μ1 − μ0)²
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass

import numpy as np
from scipy import stats

COLAS = ("superior", "inferior")
VERSION_JSON = 1


@dataclass(frozen=True)
class ConfigZ:
    mu0: float = 0.0
    mu1: float = -0.4
    sigma: float = 1.0
    n: int = 25
    alfa: float = 0.05
    cola: str = "inferior"

    def validar(self) -> None:
        if self.sigma <= 0:
            raise ValueError("σ debe ser positiva.")
        if int(self.n) != self.n or self.n < 1:
            raise ValueError("n debe ser un entero positivo.")
        if not 0 < self.alfa < 1:
            raise ValueError("α debe estar en (0, 1).")
        if self.cola not in COLAS:
            raise ValueError("cola debe ser 'superior' o 'inferior'.")
        if self.cola == "superior" and not self.mu1 > self.mu0:
            raise ValueError("Con Ha: μ > μ0, el valor específico μ1 debe ser mayor que μ0.")
        if self.cola == "inferior" and not self.mu1 < self.mu0:
            raise ValueError("Con Ha: μ < μ0, el valor específico μ1 debe ser menor que μ0.")

    @property
    def ee(self) -> float:
        return self.sigma / math.sqrt(self.n)

    @property
    def signo(self) -> int:
        return 1 if self.cola == "superior" else -1


def z_cola(a: float) -> float:
    """z_a: P(Z > z_a) = a."""
    if not 0 < a < 1:
        raise ValueError("El área debe estar en (0, 1).")
    return float(stats.norm.isf(a))


def frontera(cfg: ConfigZ) -> float:
    """k = μ0 ± z_α·EE."""
    cfg.validar()
    return cfg.mu0 + cfg.signo * z_cola(cfg.alfa) * cfg.ee


def alfa_de_frontera(cfg: ConfigZ, k):
    """α(k) = P(Ȳ ∈ RR | μ = μ0). Vectorizado en k."""
    k = np.asarray(k, dtype=float)
    if cfg.cola == "superior":
        r = stats.norm.sf(k, cfg.mu0, cfg.ee)
    else:
        r = stats.norm.cdf(k, cfg.mu0, cfg.ee)
    return float(r) if r.ndim == 0 else r


def beta_de_frontera(cfg: ConfigZ, k, mu=None):
    """β = P(Ȳ ∉ RR | μ), por defecto en μ = μ1. Vectorizado en k o en μ."""
    mu = cfg.mu1 if mu is None else mu
    k = np.asarray(k, dtype=float)
    mu = np.asarray(mu, dtype=float)
    if cfg.cola == "superior":
        r = stats.norm.cdf(k, mu, cfg.ee)
    else:
        r = stats.norm.sf(k, mu, cfg.ee)
    r = np.asarray(r)
    return float(r) if r.ndim == 0 else r


def resumen(cfg: ConfigZ, k: float | None = None) -> dict:
    """α, β y potencia para la frontera k (por defecto la que da exactamente α)."""
    k = frontera(cfg) if k is None else float(k)
    a = alfa_de_frontera(cfg, k)
    b = beta_de_frontera(cfg, k)
    return {"k": k, "ee": cfg.ee, "z_alfa": z_cola(cfg.alfa), "alfa": a, "beta": b, "potencia": 1 - b}


def estadistico(ybar, cfg: ConfigZ):
    """z = (ȳ − μ0)/(σ/√n)."""
    return (np.asarray(ybar, dtype=float) - cfg.mu0) / cfg.ee


def rechaza_z(z, cfg: ConfigZ):
    z = np.asarray(z, dtype=float)
    za = z_cola(cfg.alfa)
    return z > za if cfg.cola == "superior" else z < -za


def valor_p(z: float, cfg: ConfigZ) -> float:
    return float(stats.norm.sf(z) if cfg.cola == "superior" else stats.norm.cdf(z))


def n_requerido(mu0: float, mu1: float, sigma: float, alfa: float, beta: float) -> int:
    """Sección 10.4: n = (z_α + z_β)² σ² / (μ1 − μ0)², redondeado hacia arriba."""
    if mu1 == mu0:
        raise ValueError("μ1 debe ser distinto de μ0.")
    if sigma <= 0:
        raise ValueError("σ debe ser positiva.")
    n = (z_cola(alfa) + z_cola(beta)) ** 2 * sigma ** 2 / (mu1 - mu0) ** 2
    return int(math.ceil(n - 1e-12))


def beta_vs_n(cfg: ConfigZ, ns) -> np.ndarray:
    """β en μ1 con α fijo, para varios tamaños de muestra."""
    ns = np.asarray(ns, dtype=float)
    d = cfg.signo * (cfg.mu1 - cfg.mu0)            # distancia positiva hacia Ha
    return stats.norm.cdf(z_cola(cfg.alfa) - d * np.sqrt(ns) / cfg.sigma)


# ---------------------------------------------------------------- JSON para la segunda aplicación

def a_json(cfg: ConfigZ) -> str:
    """Configuración exportable para «Del riesgo a la evidencia: potencia y tamaño muestral»."""
    cfg.validar()
    r = resumen(cfg)
    datos = {
        "formato": "configuracion_prueba_z",
        "version": VERSION_JSON,
        "origen": "El costo de equivocarse: errores tipo I y tipo II",
        "prueba": "Z para una media, sigma conocida",
        "mu0": cfg.mu0,
        "mu1": cfg.mu1,
        "sigma": cfg.sigma,
        "n": int(cfg.n),
        "alfa": cfg.alfa,
        "tipo_prueba": cfg.cola,
        # Claves del formato anterior (config_ejemplo_Z.json), para que la segunda app las siga leyendo
        "alpha": cfg.alfa,
        "alternative": "upper" if cfg.cola == "superior" else "lower",
        "crit": r["k"],
        "hipotesis_alternativa": "mu > mu0" if cfg.cola == "superior" else "mu < mu0",
        "calculados": {
            "error_estandar": r["ee"],
            "frontera_k": r["k"],
            "beta_en_mu1": r["beta"],
            "potencia_en_mu1": r["potencia"],
        },
    }
    return json.dumps(datos, ensure_ascii=False, indent=2)


def de_json(texto: str) -> ConfigZ:
    """Acepta el formato nuevo (alfa, tipo_prueba) y el anterior (alpha, alternative = lower/upper)."""
    d = json.loads(texto)
    if "alfa" not in d and "alpha" in d:
        d["alfa"] = d["alpha"]
    if "tipo_prueba" not in d and "alternative" in d:
        d["tipo_prueba"] = {"upper": "superior", "lower": "inferior"}.get(str(d["alternative"]), d["alternative"])
    faltan = [c for c in ("mu0", "mu1", "sigma", "n", "alfa", "tipo_prueba") if c not in d]
    if faltan:
        raise ValueError(f"Faltan campos en el JSON: {', '.join(faltan)}")
    cfg = ConfigZ(float(d["mu0"]), float(d["mu1"]), float(d["sigma"]), int(d["n"]), float(d["alfa"]),
                  str(d["tipo_prueba"]))
    cfg.validar()
    return cfg


def como_dict(cfg: ConfigZ) -> dict:
    return asdict(cfg)
