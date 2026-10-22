"""Pruebas de humo de la interfaz: cada página se ejecuta sin errores.

Usa ``streamlit.testing.v1.AppTest``, que corre los scripts sin navegador.
Se pulsan los botones principales para ejecutar las simulaciones.
"""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
TIEMPO = 180


def _correr(pagina: str) -> AppTest:
    at = AppTest.from_file(str(RAIZ / "paginas" / pagina), default_timeout=TIEMPO)
    at.run()
    assert not at.exception, at.exception
    return at


def _pulsar(at: AppTest, texto: str) -> AppTest:
    for b in at.button:
        if b.label.startswith(texto):
            b.click()
            at.run()
            assert not at.exception, at.exception
            return at
    raise AssertionError(f"No se encontró el botón «{texto}»")


@pytest.mark.parametrize("pagina", ["inicio.py", "fundamentos.py", "correspondencia.py", "calculadora.py"])
def test_paginas_estaticas(pagina):
    _correr(pagina)


def test_experimento_1_varios_procedimientos():
    at = _correr("exp1_construccion.py")
    _pulsar(at, "Ejecutar simulación")
    _pulsar(at, "Ejecutar simulación")  # segunda vez: el resultado sale de la caché
    for proc in ("proporcion_wald", "dif_medias_t", "varianza_chi2", "razon_varianzas_f", "dif_proporciones"):
        at.selectbox(key="e1_proc").set_value(proc)
        at.run()
        assert not at.exception, at.exception
        _pulsar(at, "Ejecutar simulación")
    at.radio(key="e1_lado").set_value("inferior")
    at.run()
    _pulsar(at, "Ejecutar simulación")


def test_experimento_2():
    at = _correr("exp2_tamano.py")
    at.number_input(key="e2_B").set_value(100)
    at.run()
    _pulsar(at, "Ejecutar simulación")
    _pulsar(at, "Comprobar la media")


def test_experimento_3():
    at = _correr("exp3_cobertura.py")
    at.number_input(key="e3_B").set_value(2000)
    at.run()
    _pulsar(at, "Ejecutar simulación")
    at.number_input(key="e3_Bc").set_value(500)
    at.run()
    _pulsar(at, "Calcular la curva")


def test_experimento_4():
    at = _correr("exp4_nivel.py")
    _pulsar(at, "Ejecutar simulación")
    at.selectbox(key="e4_proc").set_value("proporcion_wald")
    at.run()
    _pulsar(at, "Ejecutar simulación")


@pytest.mark.parametrize("pob", ["normal", "exponencial", "t", "dado"])
def test_experimento_5(pob):
    at = _correr("exp5_distribuciones.py")
    at.selectbox(key="e5_pob_pob").set_value(pob)
    at.number_input(key="e5_B").set_value(2000)
    at.run()
    _pulsar(at, "Generar las muestras")


def test_experimento_6():
    at = _correr("exp6_supuestos.py")
    at.number_input(key="e6_B").set_value(300)
    at.run()
    _pulsar(at, "Simular el intervalo χ²")
    _pulsar(at, "Simular el intervalo t")
    _pulsar(at, "Simular")


def test_calculadora_todos_los_ejemplos_y_procedimientos():
    at = _correr("calculadora.py")
    for ej in ("8.4", "8.8", "8.11", "8.12", "8.13"):
        at.selectbox(key="calc_ej").set_value(ej)
        at.run()
        assert not at.exception, at.exception
    for proc in ("media_z_sigma", "varianza_chi2", "proporcion_wald", "dif_medias_z", "dif_proporciones",
                 "exponencial_chi2", "razon_varianzas_f"):
        at.selectbox(key="calc_proc").set_value(proc)
        at.run()
        assert not at.exception, at.exception
