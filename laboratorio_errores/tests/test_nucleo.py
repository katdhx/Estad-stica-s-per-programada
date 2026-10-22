"""Prueba Z, tamaño muestral, JSON, Monte Carlo y prueba de signos."""

import json

import numpy as np
import pytest
from scipy import stats

from nucleo import montecarlo as mc
from nucleo import pruebaz as pz
from nucleo import signos as sg


def test_frontera_da_alfa_exacto():
    for cola, mu1 in (("superior", 1.0), ("inferior", -1.0)):
        cfg = pz.ConfigZ(0.0, mu1, 2.0, 16, 0.05, cola)
        r = pz.resumen(cfg)
        assert r["alfa"] == pytest.approx(0.05, abs=1e-12)
        assert r["k"] == pytest.approx(cfg.signo * 1.6448536269514722 * 0.5)


def test_beta_formula_cerrada():
    """Superior: β = Φ(z_α − (μ1 − μ0)√n/σ)."""
    cfg = pz.ConfigZ(15, 16, 3, 36, 0.05, "superior")
    esperado = stats.norm.cdf(stats.norm.isf(0.05) - 1 * 6 / 3)
    assert pz.resumen(cfg)["beta"] == pytest.approx(esperado)
    assert float(pz.beta_vs_n(cfg, [36])[0]) == pytest.approx(esperado)


def test_mover_k_alfa_baja_beta_sube():
    cfg = pz.ConfigZ(0, 0.5, 1, 25, 0.05, "superior")
    ks = np.linspace(-0.2, 0.7, 50)
    a = pz.alfa_de_frontera(cfg, ks)
    b = pz.beta_de_frontera(cfg, ks)
    assert np.all(np.diff(a) < 0) and np.all(np.diff(b) > 0)


def test_n_requerido():
    n = pz.n_requerido(15, 16, 3, 0.05, 0.10)
    exacto = (stats.norm.isf(0.05) + stats.norm.isf(0.10)) ** 2 * 9
    assert n == int(np.ceil(exacto))
    cfg = pz.ConfigZ(15, 16, 3, n, 0.05, "superior")
    assert pz.resumen(cfg)["beta"] <= 0.10
    cfg_menos = pz.ConfigZ(15, 16, 3, n - 1, 0.05, "superior")
    assert pz.resumen(cfg_menos)["beta"] > 0.10


def test_validaciones_z():
    with pytest.raises(ValueError):
        pz.ConfigZ(0, -1, 1, 25, 0.05, "superior").validar()     # μ1 no está en Hₐ
    with pytest.raises(ValueError):
        pz.ConfigZ(0, 1, 0, 25, 0.05, "superior").validar()
    with pytest.raises(ValueError):
        pz.ConfigZ(0, 1, 1, 25, 1.2, "superior").validar()
    with pytest.raises(ValueError):
        pz.n_requerido(1, 1, 1, 0.05, 0.1)


def test_json_ida_y_vuelta_y_campos_minimos():
    cfg = pz.ConfigZ(10, 9.2, 2, 30, 0.01, "inferior")
    d = json.loads(pz.a_json(cfg))
    for campo in ("mu0", "mu1", "sigma", "n", "alfa", "tipo_prueba"):
        assert campo in d
    assert d["alternative"] == "lower" and d["alpha"] == 0.01
    assert pz.de_json(pz.a_json(cfg)) == cfg


def test_json_formato_anterior():
    viejo = {"mu0": 0.0, "mu1": -1.0, "sigma": 1.0, "n": 25, "alpha": 0.05, "alternative": "lower", "crit": -0.329}
    cfg = pz.de_json(json.dumps(viejo))
    assert cfg == pz.ConfigZ(0.0, -1.0, 1.0, 25, 0.05, "inferior")
    assert pz.frontera(cfg) == pytest.approx(-0.329, abs=1e-3)


def test_json_incompleto():
    with pytest.raises(ValueError):
        pz.de_json('{"mu0": 0}')


def test_montecarlo_z_cerca_de_lo_teorico():
    cfg = pz.ConfigZ(0, -0.4, 1, 25, 0.05, "inferior")
    df = mc.simular_z(cfg, 40000, 0.5, 1)
    r = pz.resumen(cfg)
    t = mc.resumen(df, r["alfa"], r["beta"]).set_index("Probabilidad")
    assert abs(t.loc["Error tipo I (α)", "Diferencia / EE teórico"]) < 4
    assert abs(t.loc["Error tipo II (β)", "Diferencia / EE teórico"]) < 4
    assert set(df["resultado"]) <= {mc.OK, mc.ERR1, mc.ERR2}


def test_montecarlo_clasificacion_coherente():
    cfg = pz.ConfigZ(0, 1, 1, 9, 0.1, "superior")
    df = mc.simular_z(cfg, 3000, 0.5, 2)
    h0 = df["estado"] == mc.H0_V
    rech = df["decision"] == mc.RECHAZA
    assert ((df["resultado"] == mc.ERR1) == (h0 & rech)).all()
    assert ((df["resultado"] == mc.ERR2) == (~h0 & ~rech)).all()
    assert np.allclose(df["z"], (df["media_muestral"] - 0) / (1 / 3))


def test_montecarlo_binomial_y_reproducible():
    a = mc.simular_binomial(15, 0.5, 0.3, 2, "inferior", 50000, 1.0, 5)
    assert (a["resultado"] == mc.ERR1).mean() == pytest.approx(0.00369, abs=0.0015)
    b = mc.simular_binomial(15, 0.5, 0.3, 2, "inferior", 50000, 1.0, 5)
    assert a.equals(b)
    c = mc.simular_binomial(15, 0.5, 0.3, 2, "inferior", 50000, 0.0, 5)
    assert (c["resultado"] == mc.ERR2).mean() == pytest.approx(0.873, abs=0.01)


def test_trayectoria_y_error_mc():
    df = mc.simular_binomial(15, 0.5, 0.3, 5, "inferior", 2000, 1.0, 1)
    t = mc.trayectoria(df, mc.H0_V, mc.ERR1)
    assert len(t) == 2000 and t["frecuencia"].iloc[-1] == pytest.approx((df["resultado"] == mc.ERR1).mean())
    assert mc.error_mc(0.5, 100) == pytest.approx(0.05)


@pytest.mark.parametrize("pob", list(sg.POBLACIONES))
def test_signos_alfa_no_depende_de_la_poblacion(pob):
    tasa, a = sg.tasa_rechazo(pob, 20, 0.0, 0.05, "superior", 40000, 11)
    assert abs(tasa - a) < 4 * np.sqrt(a * (1 - a) / 40000)


def test_signos_en_datos():
    r = sg.prueba([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], 0.0, 0.05, "superior")
    assert r["empates"] == 1 and r["n_usados"] == 9 and r["y"] == 9
    assert r["valor_p"] == pytest.approx(0.5 ** 9) and r["rechaza"]
