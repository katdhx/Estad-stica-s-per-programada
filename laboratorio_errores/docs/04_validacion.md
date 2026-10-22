# Validación

Resultado de `python -m pytest -v`: **61 pruebas, todas aprobadas** (Python 3.13, streamlit 1.66, scipy 1.18).

## 1. Caso del libro (SciPy)

| Cantidad | Esperado | Obtenido |
|---|---|---|
| α = P(Y ≤ 2 \| n = 15, p = .5) | 0.00369 | 0.0036926 (= 121/32 768, exacto) |
| β(.3) = P(Y > 2 \| p = .3) | 0.873 | 0.873172 |
| Potencia en .3 | 0.127 | 0.126828 |
| α con RR = {y ≤ 5} | 0.151 | 0.150879 |
| β(.3) con RR = {y ≤ 5} | 0.278 | 0.278379 |

## 2. Qué cubren las pruebas automáticas

- `test_libro.py` (14): el ejemplo de Jones, la región ampliada, coincidencia con `scipy.stats.binom`, intercambio
  α–β al mover el umbral, simetría entre cola inferior y superior, casos límite (región vacía y total), β → 1 − α
  cuando p → p₀, validación de entradas y umbral para un α máximo.
- `test_nucleo.py` (17): la frontera k da α exacto; fórmula cerrada de β; α(k) decreciente y β(k) creciente;
  n requerido es el mínimo que cumple β; validaciones; JSON de ida y vuelta, formato anterior y campos mínimos;
  Monte Carlo cerca de lo teórico (|diferencia| < 4 EE), clasificación coherente, reproducibilidad con semilla;
  prueba de signos con α independiente de la población (normal, exponencial, Cauchy, uniforme).
- `test_excel.py` (11): hojas y fórmulas, solo funciones compatibles con Excel y LibreOffice, lectura de los
  parámetros del libro (también editados), avisos con valores inválidos, Excel arbitrario con varias columnas,
  CSV con punto y coma y coma decimal, archivo que no es Excel.
- `test_paginas.py` (19): cada página corre sin excepciones ni errores, con los controles principales movidos:
  caso del libro, cambio de cola, frontera manual, simulaciones en los 6 escenarios, rondas del juego de decisión,
  libro de Excel con y sin Monte Carlo, análisis de datos subidos y carga de configuración desde Excel.

## 3. Excel contra Python

Libro generado con la configuración por defecto y 5 000 experimentos Monte Carlo, recalculado con LibreOffice
(15 632 fórmulas, 0 errores):

| Celda | Excel | Python | Diferencia |
|---|---|---|---|
| Binomial α | 0.00369263 | 0.00369263 | 0 |
| Binomial β(0.3) | 0.873172 | 0.873172 | 0 |
| Prueba_Z k | −0.328971 | −0.328971 | 6e−16 |
| Prueba_Z α | 0.05 | 0.05 | 1e−16 |
| Prueba_Z β | 0.36124 | 0.36124 | 6e−17 |
| Prueba_Z n requerido | 54 | 54 | 0 |
| Monte_Carlo errores tipo I | 103 | 103 | 0 |
| Monte_Carlo errores tipo II | 947 | 947 | 0 |
| Curva_beta β(0.30) | 0.873172 | 0.873172 | 0 |

## 4. En el navegador

Las siete páginas se abrieron en Chromium con `streamlit run app.py`, se pulsaron *Simular* y una ronda del juego
de decisión, y ninguna mostró errores.
