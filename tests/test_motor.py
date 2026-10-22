"""Pruebas del motor de Monte Carlo: corrección, reproducibilidad, memoria y errores.

Las pruebas estadísticas usan tolerancias de 4 errores estándar de Monte Carlo,
de modo que una prueba correcta falla por azar con probabilidad < 1e-4. Las
semillas son fijas, así que los resultados son deterministas.
"""

import numpy as np
import pytest

from lab import intervalos as ic
from lab import motor, teoria
from lab.poblaciones import ESPECIFICACIONES, crear


def _cob(proc, pob, n, B=20000, alfa=0.05, semilla=1, **kw):
    esc = motor.Escenario(proc, pob, n1=n, B=B, alfa=alfa, semilla=semilla, **kw)
    return motor.simular(esc).cobertura()


def _dentro(cob, objetivo, k=4.0):
    ee = np.sqrt(objetivo * (1 - objetivo) / cob.B)
    return abs(cob.estimada - objetivo) <= k * ee


# ------------------------------------------------------------- poblaciones
@pytest.mark.parametrize("clave", [k for k in ESPECIFICACIONES])
def test_momentos_de_las_poblaciones(clave):
    pob = crear(clave)
    rng = np.random.default_rng(0)
    x = pob.muestrear(rng, (400_000,))
    assert x.mean() == pytest.approx(pob.media(), abs=5 * np.sqrt(pob.varianza() / x.size))
    if clave not in ("t", "lognormal"):
        assert x.var() == pytest.approx(pob.varianza(), rel=0.02)


def test_validacion_de_poblaciones():
    assert crear("normal", sigma=-1).validar()
    assert crear("uniforme", a=2, b=1).validar()
    assert crear("bernoulli", p=1.0).validar()
    assert crear("t", nu=1.0).validar()
    assert not crear("normal").validar()


# ------------------------------------------------------- coberturas exactas
@pytest.mark.parametrize("n", [2, 5, 30])
def test_t_exacto_bajo_normalidad(n):
    assert _dentro(_cob("media_t", crear("normal", mu=3, sigma=2), n), 0.95)


@pytest.mark.parametrize("n", [1, 4, 50])
def test_z_sigma_exacto_bajo_normalidad(n):
    assert _dentro(_cob("media_z_sigma", crear("normal", mu=-1, sigma=5), n, alfa=0.10), 0.90)


@pytest.mark.parametrize("n", [3, 10, 100])
def test_chi2_exacto_bajo_normalidad(n):
    assert _dentro(_cob("varianza_chi2", crear("normal", sigma=3), n), 0.95)


@pytest.mark.parametrize("n", [1, 5, 40])
def test_pivote_exponencial_exacto(n):
    assert _dentro(_cob("exponencial_chi2", crear("exponencial", theta=10), n), 0.95)


def test_t_agrupada_exacta_con_varianzas_iguales():
    c = _cob("dif_medias_t", crear("normal", mu=1, sigma=2), 6, pob2=crear("normal", mu=0, sigma=2), n2=11)
    assert _dentro(c, 0.95)


def test_f_exacta_bajo_normalidad():
    c = _cob("razon_varianzas_f", crear("normal", sigma=1), 8, pob2=crear("normal", sigma=3), n2=12)
    assert _dentro(c, 0.95)


@pytest.mark.parametrize("lado", ["inferior", "superior"])
def test_limites_unilaterales(lado):
    c = _cob("media_t", crear("normal"), 7, lado=lado, alfa=0.05)
    assert _dentro(c, 0.95)
    c2 = _cob("varianza_chi2", crear("normal"), 7, lado=lado, alfa=0.10, semilla=3)
    assert _dentro(c2, 0.90)


def test_combinar_limites_da_1_menos_2alfa():
    """Sección 8.6, p. 412: unir límites de nivel 1 − α da un intervalo de nivel 1 − 2α."""
    esc = motor.Escenario("media_t", crear("normal"), n1=10, B=20000, alfa=0.05, semilla=9)
    est = motor.generar_estadisticos(esc)
    inf = motor.calcular_intervalos(esc, est, lado="inferior")
    sup = motor.calcular_intervalos(esc, est, lado="superior")
    ambos = inf["cubre"].to_numpy() & sup["cubre"].to_numpy()
    assert _dentro(motor.resumen_cobertura(ambos, 0.90), 0.90)


# ------------------------------------------------- coberturas aproximadas
def test_z_con_s_coincide_con_formula_exacta_bajo_normalidad():
    for n in (3, 8):
        teo = teoria.cobertura_exacta_z_s_normal(n, 0.05)
        assert teo < 0.95
        assert _dentro(_cob("media_z_s", crear("normal"), n, semilla=n), teo)


def test_wald_montecarlo_coincide_con_cobertura_exacta():
    for p, n in ((0.5, 35), (0.9, 10), (0.2, 60)):
        exacta = teoria.cobertura_exacta_wald(n, p, 0.05)
        assert _dentro(_cob("proporcion_wald", crear("bernoulli", p=p), n, semilla=int(100 * p)), exacta)


def test_wald_p_09_n_10_es_muy_malo():
    # Ejercicio 8.54: con p̂ = 1 el intervalo es el punto {1}; P(p̂ = 1) = .9^10 ≈ .349
    assert teoria.cobertura_exacta_wald(10, 0.9, 0.05) < 0.70


def test_chi2_con_exponencial_converge_al_limite_equivocado():
    lim = teoria.cobertura_limite_chi2(6.0, 0.05)
    assert lim == pytest.approx(2 * 0.8364 - 1, abs=0.002)  # 2Φ(0.98) − 1
    c = _cob("varianza_chi2", crear("exponencial", theta=1), 3000, B=3000, semilla=5)
    assert c.estimada < 0.80
    assert abs(c.estimada - lim) < 0.05


def test_t_con_exponencial_se_recupera_con_n_grande():
    c = _cob("media_t", crear("exponencial", theta=1), 500, B=20000, semilla=8)
    assert abs(c.estimada - 0.95) < 0.008


def test_t_agrupada_falla_con_varianzas_y_tamanos_distintos():
    c = _cob("dif_medias_t", crear("normal", sigma=1), 40, B=20000, pob2=crear("normal", sigma=4), n2=10, semilla=4)
    assert c.estimada < 0.85


# -------------------------------------------------------- amplitudes
def test_amplitud_z_sigma_es_deterministica():
    esc = motor.Escenario("media_z_sigma", crear("normal", sigma=2), n1=25, B=100, alfa=0.05)
    r = motor.simular(esc)
    assert np.allclose(r.tabla["amplitud"], 2 * 1.959964 * 2 / 5, rtol=1e-6)


@pytest.mark.parametrize("proc", ["media_t", "varianza_chi2"])
def test_amplitud_media_frente_a_teoria(proc):
    pob = crear("normal", sigma=2)
    n = 12
    r = motor.simular(motor.Escenario(proc, pob, n1=n, B=40000, alfa=0.05, semilla=2))
    a = r.tabla["amplitud"].to_numpy()
    teo = teoria.amplitud_esperada(proc, pob, n, 0.05)
    assert teo.exacto
    assert a.mean() == pytest.approx(teo.valor, abs=4 * a.std(ddof=1) / np.sqrt(a.size))


def test_amplitud_cae_como_raiz_de_n():
    esc = motor.Escenario("media_t", crear("exponencial", theta=10), n1=10, B=300, alfa=0.05, semilla=3)
    df = motor.barrido_n(esc, [100, 1000, 10000, 100000])
    pend = np.polyfit(np.log(df["n"]), np.log(df["amplitud_media"]), 1)[0]
    assert pend == pytest.approx(-0.5, abs=0.02)


def test_c4():
    assert teoria.c4(2) == pytest.approx(np.sqrt(2 / np.pi), rel=1e-12)
    assert teoria.c4(100_000) == pytest.approx(1.0, abs=1e-5)
    rng = np.random.default_rng(0)
    s = rng.normal(size=(200_000, 5)).std(axis=1, ddof=1)
    assert s.mean() == pytest.approx(float(teoria.c4(5)), abs=0.003)


# -------------------------------------------------- reproducibilidad
def test_misma_semilla_mismo_resultado():
    esc = motor.Escenario("media_t", crear("gamma", alpha=2), n1=17, B=500, semilla=77)
    a = motor.simular(esc).tabla
    b = motor.simular(esc).tabla
    assert a.equals(b)


def test_semillas_distintas_resultados_distintos():
    e1 = motor.Escenario("media_t", crear("normal"), n1=10, B=50, semilla=1)
    e2 = motor.Escenario("media_t", crear("normal"), n1=10, B=50, semilla=2)
    assert not np.allclose(motor.simular(e1).tabla["L"], motor.simular(e2).tabla["L"])


def test_resultado_no_depende_del_tamano_del_lote(monkeypatch):
    esc = motor.Escenario("media_t", crear("lognormal"), n1=50, B=1000, semilla=5)
    ref = motor.simular(esc).tabla
    monkeypatch.setattr(motor, "MAX_ELEMENTOS_LOTE", 777)  # lotes de 15 filas
    otra = motor.simular(esc).tabla
    assert np.allclose(ref[["L", "U"]].to_numpy(), otra[["L", "U"]].to_numpy())


def test_muestra_individual_reproduce_el_intervalo(monkeypatch):
    monkeypatch.setattr(motor, "MAX_ELEMENTOS_LOTE", 1000)
    esc = motor.Escenario("media_t", crear("exponencial"), n1=60, B=200, semilla=11)
    r = motor.simular(esc)
    for k in (1, 17, 200):
        y = motor.muestra_individual(esc, k)["y1"]
        L, U = ic.media_t(y.mean(), y.std(ddof=1), y.size, esc.alfa)
        assert L == pytest.approx(r.tabla["L"].iloc[k - 1])
        assert U == pytest.approx(r.tabla["U"].iloc[k - 1])


def test_dos_muestras_independientes_y_reproducibles():
    esc = motor.Escenario("dif_medias_t", crear("normal"), n1=5, B=300, semilla=3, pob2=crear("normal"), n2=5)
    est = motor.generar_estadisticos(esc)
    assert not np.allclose(est["media1"], est["media2"])
    d = motor.muestra_individual(esc, 10)
    assert d["y1"].mean() == pytest.approx(est["media1"][9])
    assert d["y2"].mean() == pytest.approx(est["media2"][9])


# ---------------------------------------------------- muestras grandes
def test_una_muestra_de_100000():
    esc = motor.Escenario("media_t", crear("exponencial", theta=10), n1=100_000, B=1, semilla=1)
    r = motor.simular(esc)
    assert r.tabla["amplitud"].iloc[0] == pytest.approx(2 * 1.96 * 10 / np.sqrt(1e5), rel=0.03)


def test_cien_mil_muestras():
    esc = motor.Escenario("media_t", crear("normal"), n1=5, B=100_000, semilla=1)
    c = motor.simular(esc).cobertura()
    assert c.B == 100_000
    assert c.error_estandar == pytest.approx(np.sqrt(0.95 * 0.05 / 1e5), rel=0.05)
    assert _dentro(c, 0.95)


def test_muchas_muestras_grandes_con_memoria_acotada():
    esc = motor.Escenario("media_z_sigma", crear("normal"), n1=100_000, B=200, semilla=2)
    assert motor.filas_por_lote(100_000, 200) * 100_000 <= motor.MAX_ELEMENTOS_LOTE
    r = motor.simular(esc)
    assert len(r.tabla) == 200
    assert r.tabla["estimador"].std() == pytest.approx(1 / np.sqrt(1e5), rel=0.2)


def test_trayectoria_coincide_con_calculo_directo():
    tr = motor.trayectoria_una_muestra("media_t", crear("gamma", alpha=3), 5000, 0.05, semilla=4, puntos=30)
    x = crear("gamma", alpha=3).muestrear(np.random.default_rng(4), (5000,))
    for _, f in tr.iterrows():
        k = int(f["n"])
        L, U = ic.media_t(x[:k].mean(), x[:k].std(ddof=1), k, 0.05)
        assert f["L"] == pytest.approx(L, rel=1e-9, abs=1e-9)
        assert f["U"] == pytest.approx(U, rel=1e-9, abs=1e-9)


def test_proporcion_usa_binomial_y_cuenta_bien_las_observaciones():
    esc = motor.Escenario("proporcion_wald", crear("bernoulli", p=0.3), n1=100_000, B=1000, semilla=1)
    assert esc.observaciones_totales() == 1000
    est = motor.generar_estadisticos(esc)
    assert est["exitos"].mean() / 100_000 == pytest.approx(0.3, abs=0.001)


# --------------------------------------------- parámetros inválidos
@pytest.mark.parametrize(
    "kwargs, mensaje",
    [
        (dict(procedimiento="media_t", n1=1), "≥ 2"),
        (dict(procedimiento="media_t", n1=200_000), "máximo"),
        (dict(procedimiento="media_t", B=0), "B debe"),
        (dict(procedimiento="media_t", alfa=1.2), "confianza"),
        (dict(procedimiento="media_t", lado="raro"), "Tipo"),
        (dict(procedimiento="proporcion_wald"), "no está definido"),
        (dict(procedimiento="exponencial_chi2"), "no está definido"),
        (dict(procedimiento="dif_medias_t"), "dos poblaciones"),
        (dict(procedimiento="media_t", n1=100_000, B=100_000), "límite"),
        (dict(procedimiento="inexistente"), "desconocido"),
    ],
)
def test_parametros_invalidos(kwargs, mensaje):
    base = dict(procedimiento="media_t", pob1=crear("normal"), n1=10, B=10)
    base.update(kwargs)
    esc = motor.Escenario(**base)
    errores = motor.validar_escenario(esc)
    assert errores and any(mensaje in e for e in errores)
    with pytest.raises(motor.ErrorSimulacion):
        motor.simular(esc)


def test_varianza_infinita_bloquea_z_sigma():
    esc = motor.Escenario("media_z_sigma", crear("t", nu=2), n1=10, B=10)
    assert any("varianza infinita" in e for e in motor.validar_escenario(esc))


@pytest.mark.parametrize("f, args", [
    (ic.z_critico, (0,)), (ic.z_critico, (1.5,)), (ic.t_critico, (0.05, 0)),
    (ic.media_t, (0, 1, 1, 0.05)), (ic.media_z_sigma, (0, -1, 5, 0.05)), (ic.varianza_chi2, (1, 5, 0.05, "otro")),
    (ic.n_para_proporcion, (1.2, 0.1, 0.05)),
])
def test_funciones_rechazan_argumentos_invalidos(f, args):
    with pytest.raises(ValueError):
        f(*args)


def test_cobertura_error_estandar_y_contraste():
    c = motor.resumen_cobertura(np.r_[np.ones(950), np.zeros(50)].astype(bool), 0.95)
    assert c.estimada == 0.95
    assert c.error_estandar == pytest.approx(np.sqrt(0.95 * 0.05 / 1000))
    assert c.compatible_con_nominal()
    c2 = motor.resumen_cobertura(np.r_[np.ones(900), np.zeros(100)].astype(bool), 0.95)
    assert not c2.compatible_con_nominal()
