"""Valores del libro (Wackerly, Mendenhall y Scheaffer, 7.ª ed.) y propiedades de la F."""

import numpy as np
import pytest
from scipy import stats

from nucleo import fdist, teoria


def test_ejemplo_7_7_cuantil():
    # Ejemplo 7.7 (p. 363): b = F.05(5, 9) = 3.48 (Tabla 7).
    assert fdist.f_critico(0.05, 5, 9) == pytest.approx(3.48, abs=0.005)


def test_ejercicio_7_36_doble_del_cuantil():
    # Ejercicio 7.36: si σ1² = 2σ2², S1²/S2² = 2F y b = 2·F.05(9, 7).
    b = 2 * fdist.f_critico(0.05, 9, 7)
    assert stats.f.cdf(b / 2, 9, 7) == pytest.approx(0.95)
    assert b == pytest.approx(2 * 3.68, abs=0.01)  # Tabla 7: F.05(9, 7) = 3.68


def test_ejercicio_7_29_reciproco():
    # Ejercicio 7.29: 1/F ~ F(ν2, ν1), así que F_{1−a}(ν1, ν2) = 1/F_a(ν2, ν1).
    for g1, g2 in [(5, 9), (3, 20), (12, 4)]:
        for a in (0.1, 0.05, 0.01):
            assert fdist.f_critico(1 - a, g1, g2) == pytest.approx(1 / fdist.f_critico(a, g2, g1), rel=1e-9)


def test_ejercicio_7_33_t_cuadrado():
    # Ejercicio 7.33: T² ~ F(1, ν).
    for nu in (3, 10, 40):
        t = stats.t.isf(0.025, nu)
        assert fdist.f_critico(0.05, 1, nu) == pytest.approx(t**2, rel=1e-9)


def test_ejercicio_7_34_momentos():
    # Ejercicio 7.34: E(F) = ν2/(ν2 − 2) y la varianza correspondiente.
    for g1, g2 in [(5, 9), (9, 9), (20, 30)]:
        m, v = stats.f.stats(g1, g2, moments="mv")
        assert teoria.media_f(g2) == pytest.approx(float(m))
        assert teoria.varianza_f(g1, g2) == pytest.approx(float(v))
    assert teoria.media_f(2) == float("inf")
    assert teoria.varianza_f(5, 4) == float("inf")


def test_ejercicio_8_126_intervalo():
    # Ejercicio 8.126 (p. 441): s1² = .273, s2² = .094, n1 = n2 = 10, 95 %.
    L, U = fdist.intervalo_razon(0.273, 0.094, 10, 10, 0.05)
    assert float(L) == pytest.approx(0.0855, abs=5e-4)
    assert float(U) == pytest.approx(1.386, abs=5e-3)
    assert L <= 1 <= U  # el intervalo contiene el 1


def test_intervalo_central_es_1_menos_alfa():
    a, b = fdist.intervalo_central(0.05, 12, 8)
    assert stats.f.cdf(b, 11, 7) - stats.f.cdf(a, 11, 7) == pytest.approx(0.95)


def test_intervalo_vectorizado():
    s1, s2 = np.array([1.0, 2.0]), np.array([1.0, 1.0])
    L, U = fdist.intervalo_razon(s1, s2, 10, 10, 0.05)
    assert L.shape == (2,) and L[1] == pytest.approx(L[0] / 2)


@pytest.mark.parametrize("args", [(0, 5, 9), (1, 5, 9), (0.05, 0, 9), (0.05, 5, -1)])
def test_f_critico_invalidos(args):
    with pytest.raises(ValueError):
        fdist.f_critico(*args)


@pytest.mark.parametrize("args", [(0.0, 10, 10), (0.05, 1, 10), (0.05, 10, 2.5)])
def test_intervalo_central_invalidos(args):
    with pytest.raises(ValueError):
        fdist.intervalo_central(*args)


def test_cobertura_limite():
    # Complementario: con κ = 0 se recupera 1 − α; exponencial (κ = 6) ≈ 0.673; uniforme > 1 − α.
    assert teoria.cobertura_limite(0.0, 0.05) == pytest.approx(0.95)
    assert teoria.cobertura_limite(6.0, 0.05) == pytest.approx(0.673, abs=0.002)
    assert teoria.cobertura_limite(-1.2, 0.05) > 0.95
    assert teoria.cobertura_limite(float("inf"), 0.05) == 0.0
