"""Ejemplos y ejercicios de los capítulos 7 y 8 sobre la distribución F.

Datos transcritos de Wackerly, Mendenhall y Scheaffer (7.ª ed.); páginas del libro impreso.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Ejemplo:
    clave: str
    titulo: str
    pagina: int
    enunciado: str
    tipo: str            # "cuantil" | "probabilidad" | "intervalo"
    n1: int
    n2: int
    razon_var: float     # σ1²/σ2² supuesta (para los de probabilidad y cuantil)
    s2_1: float | None = None
    s2_2: float | None = None
    confianza: float = 0.95
    resultado_libro: str = ""
    nota: str = ""


EJEMPLOS: dict[str, Ejemplo] = {
    "7.7": Ejemplo(
        "7.7", "Ejemplo 7.7: el cuantil .95 de S₁²/S₂²", 363,
        "Muestras independientes de tamaños n₁ = 6 y n₂ = 10 de dos poblaciones normales con la misma varianza. "
        "Encuentre b tal que P(S₁²/S₂² ≤ b) = .95.",
        "cuantil", 6, 10, 1.0, confianza=0.95,
        resultado_libro="b = F.05(5, 9) = 3.48 (Tabla 7).",
        nota="Aun con varianzas iguales, el cociente de las varianzas muestrales pasa de 3.48 el 5 % de las veces.",
    ),
    "7.27": Ejemplo(
        "7.27", "Ejercicio 7.27: ¿una varianza muestral el doble de la otra?", 367,
        "Con n₁ = 6, n₂ = 10 y varianzas poblacionales iguales: (a) P(S₁²/S₂² > 2); (b) P(S₁²/S₂² < 0.5); "
        "(c) la probabilidad de que una de las varianzas muestrales sea al menos el doble de la otra.",
        "probabilidad", 6, 10, 1.0,
        resultado_libro="Ejercicio con applet, sin respuesta impresa.",
    ),
    "7.36": Ejemplo(
        "7.36", "Ejercicio 7.36: cobre y plomo", 368,
        "Diez valores ln(CL50) para cobre (S₁²) y ocho para plomo (S₂²); la varianza poblacional del cobre es el doble "
        "de la del plomo. Encuentre b tal que P(S₁²/S₂² ≤ b) = .95.",
        "cuantil", 10, 8, 2.0, confianza=0.95,
        resultado_libro="Ejercicio sin respuesta impresa. Como (S₁²/σ₁²)/(S₂²/σ₂²) ~ F(9, 7) y σ₁²/σ₂² = 2, b = 2·F.05(9, 7).",
    ),
    "8.126": Ejemplo(
        "8.126", "Ejercicio 8.126: impurezas de dos proveedores", 441,
        "Diez envíos de cada proveedor: s₁² = .273 y s₂² = .094. Forme un intervalo de confianza de 95 % "
        "para la relación entre las varianzas poblacionales.",
        "intervalo", 10, 10, 1.0, s2_1=0.273, s2_2=0.094, confianza=0.95,
        resultado_libro="Ejercicio sin respuesta impresa: se usa el pivote F del Ejercicio 8.125.",
    ),
}
