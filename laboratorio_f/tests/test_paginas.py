"""Pruebas de humo de la interfaz: cada página se ejecuta sin errores.

Usa ``streamlit.testing.v1.AppTest``, que corre los scripts sin navegador, y pulsa
los botones principales para ejecutar las simulaciones (con B pequeño).
"""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
TIEMPO = 240


def _correr(pagina: str) -> AppTest:
    at = AppTest.from_file(str(RAIZ / "paginas" / pagina), default_timeout=TIEMPO)
    at.run()
    assert not at.exception, at.exception
    return at


def _pulsar(at: AppTest, texto: str) -> AppTest:
    for b in at.button:
        if b.label.startswith(texto) and not b.disabled:
            b.click()
            at.run()
            assert not at.exception, at.exception
            return at
    raise AssertionError(f"No se encontró el botón «{texto}»")


def _fijar(at: AppTest, tipo: str, clave: str, valor) -> None:
    getattr(at, tipo)(key=clave).set_value(valor)
    at.run()
    assert not at.exception, at.exception


@pytest.mark.parametrize("pagina", ["fundamentos.py", "correspondencia.py"])
def test_paginas_estaticas(pagina):
    _correr(pagina)


def test_inicio_todas_las_formas():
    at = _correr("inicio.py")
    for opcion in at.radio(key="ini_forma").options:
        _fijar(at, "radio", "ini_forma", opcion)
    _fijar(at, "select_slider", "ini_n", 50)


def test_calculadora_ejemplos_y_datos():
    at = _correr("calculadora.py")
    for clave in ("7.7", "7.27", "7.36", "8.126"):
        _fijar(at, "selectbox", "cal_ej", clave)
    _fijar(at, "text_area", "cal_y1", "1 2 tres")      # dato inválido: mensaje, no excepción
    assert at.error
    _fijar(at, "text_area", "cal_y1", "5")             # una sola observación
    assert at.error


def test_constructor():
    at = _correr("constructor.py")
    _fijar(at, "number_input", "con_B", 500)
    _pulsar(at, "Ejecutar simulación")
    _pulsar(at, "Ejecutar simulación")  # segunda vez: sale de la caché
    _fijar(at, "selectbox", "con_1_forma", "normal")
    _fijar(at, "selectbox", "con_2_forma", "t")
    _pulsar(at, "Ejecutar simulación")


def test_constructor_parametros_invalidos_bloquean():
    at = _correr("constructor.py")
    # Los controles no permiten valores fuera de rango; lo que sí puede pasar es pedir demasiados números.
    _fijar(at, "number_input", "con_n1", 20_000)
    _fijar(at, "number_input", "con_n2", 20_000)
    _fijar(at, "number_input", "con_B", 200_000)
    assert at.error
    assert any(b.disabled for b in at.button if b.label.startswith("Ejecutar"))


def test_cadena():
    at = _correr("cadena.py")
    _fijar(at, "number_input", "cad_B", 1000)
    _pulsar(at, "Ejecutar simulación")


def test_promesas():
    at = _correr("promesas.py")
    _fijar(at, "number_input", "pro_B", 1000)
    _pulsar(at, "Ejecutar simulación")
    _fijar(at, "multiselect", "pro_ns", [5, 20])
    _fijar(at, "number_input", "pro_Bn", 500)
    _pulsar(at, "Calcular las curvas")


def test_intervalo():
    at = _correr("intervalo.py")
    _fijar(at, "number_input", "int_B", 500)
    _pulsar(at, "Ejecutar simulación")
    _fijar(at, "multiselect", "int_ns", [5, 20])
    _fijar(at, "number_input", "int_Bn", 500)
    _pulsar(at, "Calcular la cobertura")


def test_mapa():
    at = _correr("mapa.py")
    _fijar(at, "number_input", "map_B", 1000)
    _fijar(at, "select_slider", "map_n", 10)
    _pulsar(at, "Simular las distribuciones")
    _fijar(at, "number_input", "map_Bp", 500)
    _pulsar(at, "Simular las 49")


def test_descubre():
    at = _correr("descubre.py")
    for clave in ("media", "una"):
        r = at.radio(key=f"des_{clave}_pred")
        _fijar(at, "radio", f"des_{clave}_pred", r.options[0])
        at.button(key=f"des_{clave}_btn").click()
        at.run()
        assert not at.exception, at.exception
