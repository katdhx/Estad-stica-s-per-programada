# Validación

Se ejecutan con `python -m pytest -v` (o `probar_windows.bat`). Resultado en el entorno de desarrollo
(Python 3.13, Linux): **80 pruebas superadas**.

## `tests/test_libro.py`: valores del libro y fórmulas

| Prueba | Qué comprueba |
|---|---|
| `test_ejemplo_7_7_cuantil` | F.05(5, 9) = 3.48 (Ejemplo 7.7, Tabla 7) |
| `test_ejercicio_7_36_doble_del_cuantil` | b = 2·F.05(9, 7) = 7.35 y P(S₁²/S₂² ≤ b) = .95 |
| `test_ejercicio_7_29_reciproco` | F₁₋ₐ(ν₁, ν₂) = 1/Fₐ(ν₂, ν₁) |
| `test_ejercicio_7_33_t_cuadrado` | F.05(1, ν) = t².025(ν) |
| `test_ejercicio_7_34_momentos` | Media y varianza de la F contra SciPy, y casos infinitos |
| `test_ejercicio_8_126_intervalo` | IC del 95 % = [0.0855, 1.386], contiene el 1 |
| `test_intervalo_central_es_1_menos_alfa` | P(F₁₋α/₂ ≤ F ≤ Fα/₂) = 1 − α |
| `test_f_critico_invalidos`, `test_intervalo_central_invalidos` | Errores claros con α, gl o n inválidos |
| `test_cobertura_limite` | κ = 0 → 0.95; exponencial → 0.673; uniforme > 0.95 |

## `tests/test_simulacion.py`: poblaciones y motor

| Prueba | Qué comprueba |
|---|---|
| `test_formas_estandarizadas` | Cada forma tiene media 0 y varianza 1 |
| `test_curtosis_y_asimetria_teoricas` | Las fórmulas de κ y asimetría coinciden con 10⁶ datos simulados (14 formas) |
| `test_densidades_integran_uno` | Las densidades dibujadas son densidades |
| `test_escala_y_posicion` | Y = μ + σX tiene media μ y varianza σ² |
| `test_parametros_invalidos` | ν ≤ 2, α ≤ 0, σ = 0, n < 2, B = 0 y exceso de memoria se rechazan |
| `test_reproducible_y_semillas_distintas` | Misma semilla → mismos resultados; otra semilla → otros |
| `test_lotes_no_cambian_el_resultado` | El tamaño del lote no altera las muestras |
| `test_insesgadez_de_s2_para_toda_forma` | E(S²) = σ² también sin normalidad (Ejemplo 8.1) |
| `test_varianza_de_s2` | V(S²) = σ⁴[2/(n−1) + κ/n] con 100 000 réplicas (error < 6 %) |
| `test_teorema_7_3_chi_cuadrado_bajo_normalidad` | W ~ χ²(n−1) y F* ~ F con normalidad (Kolmogorov–Smirnov) |
| `test_definicion_7_3_f_bajo_normalidad_con_varianzas_distintas` | F* ~ F(5, 9) con σ₁ ≠ σ₂; Ejemplo 7.7 simulado |
| `test_cobertura_exacta_bajo_normalidad` | Cobertura ≈ 1 − α con (n₁, n₂, α) distintos, incluido n = 200 |
| `test_cobertura_igual_a_probabilidad_central_de_F` | El intervalo acierta exactamente en las réplicas con F* en el centro |
| `test_colas_pesadas_rompen_la_cobertura_y_no_se_arregla_con_n` | Exponencial < 0.80 con n = 10, 100, 1000 y ≈ límite con n = 1000 |
| `test_colas_livianas_sobrecubren` | Uniforme > 0.98 |
| `test_la_media_no_influye` | Sumar 50 a los datos no cambia S² |
| `test_proporcion`, `test_barridos`, `test_muestra_grande_de_n` | Error estándar Monte Carlo, barridos y n = 20 000 |

Criterio para las pruebas estadísticas: diferencia menor que 3.5 errores estándar Monte Carlo (o un valor p de
Kolmogorov–Smirnov mayor que 0.001), con semillas fijas para que el resultado sea reproducible.

## `tests/test_paginas.py`: interfaz

Con `streamlit.testing.v1.AppTest` se ejecuta cada página, se cambian controles y se pulsan los botones de
simulación (Inicio con todas las formas; Calculadora con los cuatro ejemplos y con datos inválidos; Experimentos
1 a 6, incluidos los barridos por n, el mapa de robustez, las 49 parejas y los experimentos guiados). Ninguna
página debe lanzar una excepción, y una simulación demasiado grande debe bloquear el botón con un mensaje.

## Comprobaciones visuales

Todas las páginas se revisaron en el navegador después de ejecutar sus simulaciones.
