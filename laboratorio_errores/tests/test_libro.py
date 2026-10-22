"""Validación contra el ejemplo de Jones (Sección 10.2) con SciPy."""

import pytest
from scipy import stats

from nucleo import binomial as bn


def test_jones_region_libro():
    """n = 15, p0 = .5, p1 = .3, RR = {y ≤ 2}."""
    a = bn.alfa(15, 0.5, 2)
    b = bn.beta(15, 0.3, 2)
    assert a == pytest.approx(0.00369, abs=5e-6)
    assert a == pytest.approx(121 / 32768, rel=1e-12)          # (1 + 15 + 105) / 2^15, exacto
    assert b == pytest.approx(0.873, abs=5e-4)
    assert 1 - b == pytest.approx(0.127, abs=5e-4)
    assert bn.potencia(15, 0.3, 2) == pytest.approx(1 - b)


def test_jones_region_ampliada():
    """La otra región que compara el libro: RR = {y ≤ 5}."""
    assert bn.alfa(15, 0.5, 5) == pytest.approx(0.151, abs=5e-4)
    assert bn.beta(15, 0.3, 5) == pytest.approx(0.278, abs=5e-4)


def test_coincide_con_scipy_directo():
    for n, p0, p1, c in [(15, 0.5, 0.3, 2), (20, 0.4, 0.2, 4), (8, 0.6, 0.1, 0)]:
        assert bn.alfa(n, p0, c) == pytest.approx(stats.binom.cdf(c, n, p0))
        assert bn.beta(n, p1, c) == pytest.approx(1 - stats.binom.cdf(c, n, p1))


def test_intercambio_alfa_beta():
    """Al agrandar la región de rechazo α sube y β baja (n fijo)."""
    alfas = [bn.alfa(15, 0.5, c) for c in range(16)]
    betas = [bn.beta(15, 0.3, c) for c in range(16)]
    assert all(x < y for x, y in zip(alfas, alfas[1:]))
    assert all(x > y for x, y in zip(betas, betas[1:]))


def test_cola_superior_es_espejo():
    """Contar éxitos o fracasos: y ≤ c con p equivale a y ≥ n − c con 1 − p."""
    for c in range(0, 16):
        assert bn.alfa(15, 0.5, c, "inferior") == pytest.approx(bn.alfa(15, 0.5, 15 - c, "superior"))
        assert bn.beta(15, 0.3, c, "inferior") == pytest.approx(bn.beta(15, 0.7, 15 - c, "superior"))


def test_casos_limite():
    assert bn.alfa(10, 0.5, -1) == 0.0          # región vacía: nunca se rechaza
    assert bn.beta(10, 0.3, -1) == 1.0
    assert bn.alfa(10, 0.5, 10) == pytest.approx(1.0)   # región total: siempre se rechaza
    assert bn.beta(10, 0.3, 10) == pytest.approx(0.0)
    assert bn.alfa(10, 0.5, 11, "superior") == 0.0
    assert bn.alfa(10, 0.5, 0, "superior") == pytest.approx(1.0)


def test_beta_cerca_de_p0_tiende_a_uno_menos_alfa():
    a = bn.alfa(15, 0.5, 2)
    assert bn.beta(15, 0.4999999, 2) == pytest.approx(1 - a, abs=1e-6)


@pytest.mark.parametrize("args", [(0, 0.5, 2, "inferior"), (15, 0, 2, "inferior"), (15, 1, 2, "inferior"),
                                  (15, 0.5, 2.5, "inferior"), (15, 0.5, 16, "inferior"), (15, 0.5, 2, "otra")])
def test_validacion(args):
    with pytest.raises(ValueError):
        bn.validar(*args)


def test_umbral_para_alfa():
    c = bn.umbral_para_alfa(15, 0.5, 0.05)
    assert bn.alfa(15, 0.5, c) <= 0.05 < bn.alfa(15, 0.5, c + 1)
    assert c == 3
