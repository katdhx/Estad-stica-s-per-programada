"""Reproducción de los resultados numéricos impresos en los capítulos 7 y 8.

Si una fórmula de la app estuviera mal, estos ejemplos del libro lo detectarían.
Las tolerancias reflejan el redondeo de las tablas del libro (3–4 cifras).
"""

import numpy as np
import pytest
from scipy import stats

from lab import intervalos as ic
from lab.ejemplos_libro import EJEMPLOS, estadisticos_desde
from lab.procedimientos import PROCEDIMIENTOS


@pytest.mark.parametrize("clave", list(EJEMPLOS))
def test_ejemplos_del_libro(clave):
    ej = EJEMPLOS[clave]
    e = estadisticos_desde(ej.procedimiento, ej.datos)
    _, L, U = PROCEDIMIENTOS[ej.procedimiento].calcular(e, 1 - ej.confianza, "bilateral", None, None)
    assert float(L) == pytest.approx(ej.esperado[0], abs=ej.tolerancia)
    assert float(U) == pytest.approx(ej.esperado[1], abs=ej.tolerancia)


def test_ejemplo_8_11_estadisticos():
    y = np.array(EJEMPLOS["8.11"].datos["y"], float)
    assert y.mean() == pytest.approx(2959, abs=0.5)
    assert y.std(ddof=1) == pytest.approx(39.1, abs=0.05)
    L, U = ic.media_t(y.mean(), y.std(ddof=1), 8, 0.05)
    assert (U - L) / 2 == pytest.approx(32.7, abs=0.05)


def test_ejemplo_8_12_varianza_agrupada():
    a = np.array(EJEMPLOS["8.12"].datos["y1"], float)
    b = np.array(EJEMPLOS["8.12"].datos["y2"], float)
    assert a.mean() == pytest.approx(35.22, abs=0.005)
    assert b.mean() == pytest.approx(31.56, abs=0.005)
    sp2 = ic.varianza_agrupada(a.var(ddof=1), b.var(ddof=1), 9, 9)
    assert sp2 == pytest.approx(22.236, abs=0.002)
    # n1 = n2: S_p^2 es el promedio simple (p. 429)
    assert sp2 == pytest.approx((a.var(ddof=1) + b.var(ddof=1)) / 2)


def test_ejemplo_8_4_pivote_exponencial_n1():
    # Ejemplo 8.4: a = .051, b = 2.996 con U = Y/θ ~ Exp(1)
    a = -np.log(0.95)
    b = -np.log(0.05)
    assert a == pytest.approx(0.051, abs=0.0005)
    assert b == pytest.approx(2.996, abs=0.0005)
    # El pivote 2Y/θ ~ χ²(2) (Ejercicio 8.46) da exactamente el mismo intervalo.
    L, U = ic.exponencial_chi2(1.0, 1, 0.10)
    assert L == pytest.approx(1 / b, rel=1e-9)
    assert U == pytest.approx(1 / a, rel=1e-9)


def test_ejemplo_7_2_probabilidad():
    # P(|Ȳ − μ| ≤ .3) con σ = 1, n = 9 → P(−.9 ≤ Z ≤ .9) = .6318
    p = stats.norm.cdf(0.9) - stats.norm.cdf(-0.9)
    assert p == pytest.approx(0.6318, abs=0.0001)


def test_ejemplo_7_3_tamano():
    assert ic.n_para_media(1.0, 0.3, 0.05) == 43


def test_ejemplo_7_5_intervalo_de_s2():
    a1, a2 = ic.chi2_critico(0.95, 9), ic.chi2_critico(0.05, 9)
    assert a1 / 9 == pytest.approx(0.369, abs=0.0005)
    assert a2 / 9 == pytest.approx(1.880, abs=0.0005)


def test_ejemplo_7_6_t():
    assert ic.t_critico(0.05, 5) == pytest.approx(2.015, abs=0.0005)
    assert stats.norm.cdf(2) - stats.norm.cdf(-2) == pytest.approx(0.9544, abs=0.0001)


def test_ejemplo_7_8_y_7_9_tcl():
    assert stats.norm.cdf(-2.5) == pytest.approx(0.0062, abs=0.0001)
    assert stats.norm.cdf(-3) == pytest.approx(0.0013, abs=0.0001)


def test_ejemplo_7_10_y_7_11_binomial():
    assert stats.norm.sf(1) == pytest.approx(0.1587, abs=0.0001)
    assert stats.binom.cdf(8, 25, 0.4) == pytest.approx(0.274, abs=0.0005)
    assert stats.binom.pmf(8, 25, 0.4) == pytest.approx(0.120, abs=0.0005)
    aprox = stats.norm.cdf(8.5, 10, np.sqrt(6))
    assert aprox == pytest.approx(0.2709, abs=0.002)


def test_ejemplos_8_9_y_8_10_tamano_muestral():
    assert ic.n_para_proporcion(0.6, 0.04, 0.10) == 406
    assert ic.n_para_proporcion(0.5, 0.04, 0.10) == 423
    assert ic.n_para_dif_medias(2, 2, 1, 0.05) == 31


def test_ejemplo_8_2_limite_error():
    b = 2 * np.sqrt(0.56 * 0.44 / 1000)
    assert b == pytest.approx(0.03, abs=0.0015)


def test_ejemplo_8_3_error_estandar():
    ee = np.sqrt(1_440_000 / 100 + 1_960_000 / 100)
    assert ee == pytest.approx(184.4, abs=0.05)


def test_figura_8_8_primer_intervalo():
    # p̂ = 18/35, intervalo (.3487, .6799)
    L, U = ic.proporcion_wald(18 / 35, 35, 0.05)
    assert L == pytest.approx(0.3487, abs=0.0005)
    assert U == pytest.approx(0.6799, abs=0.0005)


@pytest.mark.parametrize(
    "funcion, args, libro, tol",
    [
        (ic.z_critico, (0.05,), 1.645, 0.0005),
        (ic.z_critico, (0.025,), 1.96, 0.0005),
        (ic.z_critico, (0.01,), 2.33, 0.005),
        (ic.t_critico, (0.10, 21), 1.323, 0.0005),
        (ic.t_critico, (0.025, 7), 2.365, 0.0005),
        (ic.t_critico, (0.025, 16), 2.120, 0.0005),
        (ic.chi2_critico, (0.90, 10), 4.86518, 0.00001),
        (ic.chi2_critico, (0.05, 6), 12.5916, 0.0001),
        (ic.chi2_critico, (0.05, 9), 16.919, 0.0005),
        (ic.chi2_critico, (0.95, 9), 3.325, 0.0005),
        (ic.chi2_critico, (0.05, 2), 5.991, 0.0005),
        (ic.chi2_critico, (0.95, 2), 0.103, 0.0005),
        (ic.f_critico, (0.05, 5, 9), 3.48, 0.005),
        (ic.f_critico, (0.100, 5, 7), 2.88, 0.005),
        (ic.f_critico, (0.050, 5, 7), 3.97, 0.005),
        (ic.f_critico, (0.025, 5, 7), 5.29, 0.005),
        (ic.f_critico, (0.010, 5, 7), 7.46, 0.005),
        (ic.f_critico, (0.005, 5, 7), 9.52, 0.005),
    ],
)
def test_valores_criticos_de_las_tablas(funcion, args, libro, tol):
    assert funcion(*args) == pytest.approx(libro, abs=tol)
