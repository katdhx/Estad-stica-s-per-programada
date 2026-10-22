"""Poblaciones, motor de Monte Carlo y comparación con la teoría."""

import numpy as np
import pytest
from scipy import stats

from nucleo import fdist, motor, teoria
from nucleo.poblaciones import CATALOGO_ROBUSTEZ, FORMAS, Poblacion, forma


def _z(est, teo, ee):
    return abs(est - teo) / ee


# ---------- poblaciones ----------

@pytest.mark.parametrize("clave", list(FORMAS))
def test_formas_estandarizadas(clave):
    f = forma(clave)
    x = f.muestrear(np.random.default_rng(1), (400_000,))
    assert abs(x.mean()) < 0.02
    assert x.var() == pytest.approx(1.0, abs=0.03)


@pytest.mark.parametrize("f", CATALOGO_ROBUSTEZ, ids=lambda f: f.nombre_corto())
def test_curtosis_y_asimetria_teoricas(f):
    x = f.muestrear(np.random.default_rng(2), (1_000_000,))
    assert stats.skew(x) == pytest.approx(f.asimetria(), abs=0.05 + 0.1 * abs(f.asimetria()))
    if f.curtosis() < 3:  # con curtosis grande la estimación es demasiado ruidosa
        assert stats.kurtosis(x) == pytest.approx(f.curtosis(), abs=0.1 + 0.1 * abs(f.curtosis()))


@pytest.mark.parametrize("f", CATALOGO_ROBUSTEZ, ids=lambda f: f.nombre_corto())
def test_densidades_integran_uno(f):
    xs = np.linspace(-30, 60, 400_001)
    with np.errstate(all="ignore"):
        y = np.nan_to_num(f.densidad()(xs), nan=0.0, posinf=0.0)
    assert np.trapezoid(y, xs) == pytest.approx(1.0, abs=0.01)


def test_escala_y_posicion():
    p = Poblacion(forma("exponencial"), sigma=3.0, mu=5.0)
    y = p.muestrear(np.random.default_rng(3), (500_000,))
    assert p.varianza == 9.0
    assert y.mean() == pytest.approx(5.0, abs=0.03) and y.var() == pytest.approx(9.0, rel=0.02)


def test_parametros_invalidos():
    assert forma("t", 2.0).validar()          # t necesita ν > 2 para tener varianza
    assert forma("gamma", -1.0).validar()
    assert Poblacion(forma("normal"), sigma=0).validar()
    esc = motor.Escenario(Poblacion(forma("normal")), Poblacion(forma("normal")), 1, 10, 100)
    assert esc.validar()
    assert motor.Escenario(Poblacion(forma("normal")), Poblacion(forma("normal")), 10, 10, 0).validar()
    grande = motor.Escenario(Poblacion(forma("normal")), Poblacion(forma("normal")), 20_000, 20_000, 200_000)
    assert any("límite" in e for e in grande.validar())
    with pytest.raises(ValueError):
        motor.simular(esc)


# ---------- motor ----------

def _esc(f1="normal", f2="normal", n1=10, n2=10, B=40_000, s1=1.0, s2=1.0, semilla=7):
    return motor.Escenario(Poblacion(forma(f1), s1), Poblacion(forma(f2), s2), n1, n2, B, semilla)


def test_reproducible_y_semillas_distintas():
    a, b = motor.simular(_esc(B=2000)), motor.simular(_esc(B=2000))
    c = motor.simular(_esc(B=2000, semilla=8))
    assert np.array_equal(a.s2_1, b.s2_1) and np.array_equal(a.s2_2, b.s2_2)
    assert not np.array_equal(a.s2_1, c.s2_1)


def test_lotes_no_cambian_el_resultado(monkeypatch):
    a = motor.simular(_esc(B=3000))
    monkeypatch.setattr(motor, "MAX_LOTE", 997)
    b = motor.simular(_esc(B=3000))
    np.testing.assert_allclose(a.s2_1, b.s2_1)


def test_insesgadez_de_s2_para_toda_forma():
    # Ejemplo 8.1: E(S²) = σ² sin importar la forma.
    for clave in ("normal", "exponencial", "uniforme"):
        r = motor.simular(_esc(clave, clave, n1=8, n2=8, s1=2.0, s2=0.5))
        assert _z(r.s2_1.mean(), 4.0, r.s2_1.std() / np.sqrt(r.s2_1.size)) < 4
        assert _z(r.s2_2.mean(), 0.25, r.s2_2.std() / np.sqrt(r.s2_2.size)) < 4


@pytest.mark.parametrize("clave,n", [("normal", 10), ("exponencial", 10), ("uniforme", 30), ("gamma", 20)])
def test_varianza_de_s2(clave, n):
    # Complementario: V(S²) = σ⁴[2/(n−1) + κ/n].
    f = forma(clave)
    r = motor.simular(motor.Escenario(Poblacion(f), Poblacion(f), n, n, 100_000, 11))
    assert r.s2_1.var() == pytest.approx(teoria.varianza_s2(1.0, n, f.curtosis()), rel=0.06)


def test_teorema_7_3_chi_cuadrado_bajo_normalidad():
    r = motor.simular(_esc(n1=6, n2=6, B=60_000))
    assert stats.kstest(r.W1, stats.chi2(5).cdf).pvalue > 0.001
    assert teoria.ks_distancia(r.F_pivote, 5, 5) < 0.01


def test_definicion_7_3_f_bajo_normalidad_con_varianzas_distintas():
    r = motor.simular(_esc(n1=6, n2=10, s1=3.0, s2=0.5, B=60_000))
    assert stats.kstest(r.F_pivote, stats.f(5, 9).cdf).pvalue > 0.001
    # Ejemplo 7.7 con σ1 = σ2 se mide con el cociente S1²/S2²:
    r2 = motor.simular(_esc(n1=6, n2=10, B=60_000))
    p = motor.cola_superior(r2, 0.05)
    assert abs(p.z()) < 3.5
    assert np.allclose(r2.F_cociente, r2.F_pivote)


def test_cobertura_exacta_bajo_normalidad():
    for n1, n2, alfa in [(5, 5, 0.05), (12, 30, 0.10), (200, 200, 0.01)]:
        c = motor.cobertura(motor.simular(_esc(n1=n1, n2=n2, B=40_000, s1=2.0)), alfa)
        assert abs(c.z()) < 3.5, (n1, n2, alfa, c.estimada)


def test_cobertura_igual_a_probabilidad_central_de_F():
    # Sección 8.5: el intervalo contiene σ2²/σ1² ⇔ F_{1−α/2} ≤ F* ≤ F_{α/2}.
    r = motor.simular(_esc("exponencial", "t", n1=15, n2=9, B=20_000, s1=1.5, s2=0.7))
    E = r.escenario
    L, U = fdist.intervalo_razon(r.s2_1, r.s2_2, E.n1, E.n2, 0.05)
    theta = E.pob2.varianza / E.pob1.varianza
    a, b = fdist.intervalo_central(0.05, E.n1, E.n2)
    np.testing.assert_array_equal((L <= theta) & (theta <= U), (a <= r.F_pivote) & (r.F_pivote <= b))
    assert motor.cobertura(r, 0.05).aciertos == int(((L <= theta) & (theta <= U)).sum())


def test_colas_pesadas_rompen_la_cobertura_y_no_se_arregla_con_n():
    c = [motor.cobertura(motor.simular(_esc("exponencial", "exponencial", n1=n, n2=n, B=20_000)), 0.05).estimada
         for n in (10, 100, 1000)]
    assert all(v < 0.80 for v in c)
    assert c[2] == pytest.approx(teoria.cobertura_limite(6.0, 0.05), abs=0.02)


def test_colas_livianas_sobrecubren():
    c = motor.cobertura(motor.simular(_esc("uniforme", "uniforme", n1=30, n2=30, B=20_000)), 0.05)
    assert c.estimada > 0.98


def test_la_media_no_influye():
    a = motor.simular(motor.Escenario(Poblacion(forma("normal"), 1, 0), Poblacion(forma("normal")), 10, 10, 5000, 3))
    b = motor.simular(motor.Escenario(Poblacion(forma("normal"), 1, 50), Poblacion(forma("normal")), 10, 10, 5000, 3))
    np.testing.assert_allclose(a.s2_1, b.s2_1, rtol=1e-9)


def test_proporcion():
    p = motor.Proporcion(950, 1000, 0.95)
    assert p.estimada == 0.95 and p.error_estandar == pytest.approx(np.sqrt(0.95 * 0.05 / 1000))
    assert p.compatible() and not motor.Proporcion(700, 1000, 0.95).compatible()


def test_barridos():
    df = motor.barrido_n(forma("normal"), forma("normal"), [5, 50], 3000, 0.05, 1)
    assert list(df["n1"]) == [5, 50] and df["cobertura"].between(0.92, 0.98).all()
    dff = motor.barrido_formas([forma("normal"), forma("exponencial")], 30, 3000, 0.05, 1)
    assert dff.loc[dff["clave"] == "exponencial", "cobertura"].iloc[0] < dff.loc[dff["clave"] == "normal", "cobertura"].iloc[0]
    dfp = motor.barrido_parejas([forma("normal"), forma("exponencial")], 20, 1000, 0.05, 1)
    assert len(dfp) == 4


def test_muestra_grande_de_n():
    # n grande con pocas réplicas: S² se concentra en σ².
    r = motor.simular(_esc(n1=20_000, n2=20_000, B=50, s1=2.0))
    assert np.abs(r.s2_1 - 4.0).max() < 0.2
