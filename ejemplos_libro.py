"""Ejemplos numéricos del libro usados para validar el código.

Los datos y los resultados esperados se transcribieron directamente de
Wackerly, Mendenhall y Scheaffer (7.ª ed.). Los resultados del libro se
calcularon con tablas de cuatro cifras (p. ej., z_.01 = 2.33 en lugar de
2.3263), así que las pruebas comparan con la tolerancia que esas tablas
permiten. Esto se indica en cada caso.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class EjemploLibro:
    clave: str
    titulo: str
    pagina: int
    procedimiento: str
    enunciado: str
    confianza: float
    datos: dict = field(default_factory=dict)          # datos crudos o resúmenes
    esperado: tuple[float, float] | None = None        # (L, U) publicado en el libro
    tolerancia: float = 0.0                            # por redondeo de tablas
    nota: str = ""


EJEMPLOS: dict[str, EjemploLibro] = {
    "8.7": EjemploLibro(
        clave="8.7",
        titulo="Ejemplo 8.7: tiempos de compra",
        pagina=412,
        procedimiento="media_z_s",
        enunciado=(
            "Se registraron los tiempos de compra de n = 64 clientes. El promedio y la varianza "
            "fueron 33 minutos y 256 minutos². Estime μ con coeficiente de confianza .90."
        ),
        confianza=0.90,
        datos={"n": 64, "media": 33.0, "var": 256.0},
        esperado=(29.71, 36.29),
        tolerancia=0.01,
        nota=(
            "El libro usa z.05 = 1.645. Al final del ejemplo dice «aproximadamente 95 %», pero el "
            "intervalo es del 90 %: es una errata del texto."
        ),
    ),
    "8.8": EjemploLibro(
        clave="8.8",
        titulo="Ejemplo 8.8: fallas de refrigeradores",
        pagina=413,
        procedimiento="dif_proporciones",
        enunciado=(
            "Marca A: 12 fallas en 50 refrigeradores. Marca B: 12 fallas en 60. "
            "Estime p₁ − p₂ con coeficiente de confianza de aproximadamente .98."
        ),
        confianza=0.98,
        datos={"n1": 50, "exitos1": 12, "n2": 60, "exitos2": 12},
        esperado=(-0.1451, 0.2251),
        tolerancia=0.001,
        nota="El libro redondea z.01 = 2.33; con z.01 = 2.3263 el margen es .1848 en lugar de .1851.",
    ),
    "8.11": EjemploLibro(
        clave="8.11",
        titulo="Ejemplo 8.11: velocidad de proyectiles",
        pagina=426,
        procedimiento="media_t",
        enunciado=(
            "Velocidades en la boca del cañón (pies/s) de ocho proyectiles. Encuentre un intervalo de "
            "confianza de 95 % para la velocidad media, suponiendo normalidad."
        ),
        confianza=0.95,
        datos={"y": [3005, 2925, 2935, 2965, 2995, 3005, 2937, 2905]},
        esperado=(2959 - 32.7, 2959 + 32.7),
        tolerancia=0.15,
        nota="El libro redondea ȳ = 2959 y s = 39.1, y usa t.025,7 = 2.365.",
    ),
    "8.12": EjemploLibro(
        clave="8.12",
        titulo="Ejemplo 8.12: métodos de capacitación",
        pagina=428,
        procedimiento="dif_medias_t",
        enunciado=(
            "Tiempos de ensamble (minutos) de dos grupos de nueve obreros: procedimiento estándar y "
            "nuevo. Estime μ₁ − μ₂ con coeficiente .95, suponiendo normalidad y varianzas iguales."
        ),
        confianza=0.95,
        datos={
            "y1": [32, 37, 35, 28, 41, 44, 35, 31, 34],
            "y2": [35, 31, 29, 25, 34, 40, 27, 32, 31],
        },
        esperado=(-1.05, 8.37),
        tolerancia=0.015,
        nota="El libro obtiene 3.66 ± 4.71 con t.025,16 = 2.120 y s_p = 4.716.",
    ),
    "8.13": EjemploLibro(
        clave="8.13",
        titulo="Ejemplo 8.13: variabilidad de un equipo de audio",
        pagina=435,
        procedimiento="varianza_chi2",
        enunciado=(
            "Tres mediciones independientes del volumen de una misma fuente: 4.1, 5.2 y 10.2. "
            "Estime σ² con coeficiente de confianza .90, suponiendo normalidad."
        ),
        confianza=0.90,
        datos={"y": [4.1, 5.2, 10.2]},
        esperado=(3.53, 205.24),
        tolerancia=1.0,
        nota=(
            "El libro usa χ².95 = .103 (tabla) en lugar de .1026; por eso su límite superior es "
            "205.24 y el valor exacto es ≈ 206.0."
        ),
    ),
    "8.4": EjemploLibro(
        clave="8.4",
        titulo="Ejemplo 8.4: una observación exponencial",
        pagina=407,
        procedimiento="exponencial_chi2",
        enunciado=(
            "Con una sola observación Y de una exponencial de media θ, construya un intervalo de "
            "confianza de 90 % para θ. El libro obtiene (Y/2.996, Y/.051)."
        ),
        confianza=0.90,
        datos={"y": [1.0]},
        esperado=(1 / 2.996, 1 / 0.051),
        tolerancia=0.15,
        nota="Con Y = 1. El libro redondea a = .051; el valor exacto es −ln(.95) = .0513.",
    ),
}


def estadisticos_desde(clave: str, d: dict) -> dict:
    """Convierte datos crudos o resúmenes en el diccionario de estadísticos de un procedimiento."""
    if clave in ("media_t", "media_z_s", "media_z_sigma", "varianza_chi2", "exponencial_chi2"):
        if "y" in d:
            y = np.asarray(d["y"], float)
            return {"n": y.size, "media": y.mean(), "var": y.var(ddof=1) if y.size > 1 else np.nan, "suma": y.sum()}
        return {"n": d["n"], "media": d["media"], "var": d.get("var", np.nan), "suma": d["media"] * d["n"]}
    if clave in ("dif_medias_t", "dif_medias_z", "razon_varianzas_f"):
        if "y1" in d:
            a, b = np.asarray(d["y1"], float), np.asarray(d["y2"], float)
            return {"n1": a.size, "media1": a.mean(), "var1": a.var(ddof=1), "n2": b.size, "media2": b.mean(), "var2": b.var(ddof=1)}
        return d
    return d
