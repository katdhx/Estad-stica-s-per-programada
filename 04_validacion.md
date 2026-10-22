# Validación matemática y computacional

Este documento registra la ejecución **real** de las pruebas automáticas (no son resultados inventados). Para repetirla
en Windows: doble clic en `probar_windows.bat`, o `python -m pytest -v` en la carpeta del proyecto.

## Entornos en los que se ejecutó

| Entorno | Python | streamlit | numpy | scipy | pandas | plotly | Resultado |
|---|---|---|---|---|---|---|---|
| Actual | 3.13 | 1.66.0 | 2.5.3 | 1.18.1 | 3.0.5 | 7.1.0 | 117 de 117 pasan |
| Versiones anteriores | 3.13 | 1.40.2 | 2.1.3 | 1.14.1 | 2.2.3 | 5.24.1 | 117 de 117 pasan |

(Ejecutado en Linux en el entorno de desarrollo. El código no depende del sistema operativo; en Windows se recomienda
correr `probar_windows.bat` una vez después de instalar.)

## Qué se verifica

| Archivo | Qué prueba | Cómo |
|---|---|---|
| `tests/test_libro.py` | Fórmulas de los intervalos | Reproducen los Ejemplos 8.4, 8.7, 8.8, 8.11, 8.12 y 8.13 con la tolerancia del redondeo de las tablas del libro. |
| | Valores críticos y grados de libertad | 18 valores de las Tablas 4–7 citados en el capítulo 7 (z, t con 5, 7, 16 y 21 gl, χ² con 2, 6, 9 y 10 gl, F con (5, 7) y (5, 9) gl). |
| | Otros resultados numéricos | Ejemplos 7.2, 7.3, 7.5, 7.6, 7.8–7.11, 8.2, 8.3, 8.9, 8.10 y el primer intervalo de la Figura 8.8. |
| `tests/test_motor.py` | Poblaciones | Media y varianza simuladas de cada población frente a sus fórmulas. |
| | Coberturas exactas | t, Z, χ², pivote exponencial, t agrupada y F bajo sus supuestos: cobertura dentro de ±4 errores estándar de 1 − α (B = 20 000). |
| | Límites unilaterales | Cobertura 1 − α; unir dos límites de nivel 1 − α da 1 − 2α (Sección 8.6, p. 412). |
| | Coberturas conocidas sin simular | Monte Carlo frente a la cobertura exacta del intervalo de Wald (suma binomial) y de Z con S bajo normalidad (P(\|T\| ≤ z)). |
| | Violación de supuestos | χ² con exponencial converge a ≈ 0.673; t con exponencial se recupera con n = 500; t agrupada falla con n₁ ≠ n₂ y σ₁ ≠ σ₂. |
| | Amplitudes | Z con σ: amplitud determinística 2zσ/√n. t y χ²: media simulada frente a E(amplitud) teórica. Pendiente log-log −1/2 ± 0.02 hasta n = 100 000. c₄(n) frente a simulación. |
| | Reproducibilidad | Misma semilla, mismos resultados; semillas distintas, resultados distintos; resultado independiente del tamaño de lote; la muestra individual regenerada reproduce su intervalo. |
| | Muestras grandes | n = 100 000 con B = 1; B = 100 000 con n = 5; 200 muestras de 100 000 con memoria acotada; proporciones con n = 100 000. |
| | Manejo de errores | 10 escenarios inválidos (n, B, nivel, tipo, población incompatible, dos muestras incompletas, límite n × B, procedimiento inexistente) y 7 llamadas inválidas a funciones; σ² infinita bloquea el intervalo Z. |
| `tests/test_paginas.py` | Interfaz | Cada página se ejecuta sin errores (con `streamlit.testing`) y se pulsan sus botones con varios procedimientos y poblaciones. |

Las pruebas estadísticas usan semillas fijas (son deterministas) y una tolerancia de 4 errores estándar: si el
código fuera correcto pero la semilla cambiara, la probabilidad de fallo por azar sería menor que 1 en 15 000.

## Salida de la ejecución

```
tests/test_libro.py::test_ejemplos_del_libro[8.7] PASSED
tests/test_libro.py::test_ejemplos_del_libro[8.8] PASSED
tests/test_libro.py::test_ejemplos_del_libro[8.11] PASSED
tests/test_libro.py::test_ejemplos_del_libro[8.12] PASSED
tests/test_libro.py::test_ejemplos_del_libro[8.13] PASSED
tests/test_libro.py::test_ejemplos_del_libro[8.4] PASSED
tests/test_libro.py::test_ejemplo_8_11_estadisticos PASSED
tests/test_libro.py::test_ejemplo_8_12_varianza_agrupada PASSED
tests/test_libro.py::test_ejemplo_8_4_pivote_exponencial_n1 PASSED
tests/test_libro.py::test_ejemplo_7_2_probabilidad PASSED
tests/test_libro.py::test_ejemplo_7_3_tamano PASSED
tests/test_libro.py::test_ejemplo_7_5_intervalo_de_s2 PASSED
tests/test_libro.py::test_ejemplo_7_6_t PASSED
tests/test_libro.py::test_ejemplo_7_8_y_7_9_tcl PASSED
tests/test_libro.py::test_ejemplo_7_10_y_7_11_binomial PASSED
tests/test_libro.py::test_ejemplos_8_9_y_8_10_tamano_muestral PASSED
tests/test_libro.py::test_ejemplo_8_2_limite_error PASSED
tests/test_libro.py::test_ejemplo_8_3_error_estandar PASSED
tests/test_libro.py::test_figura_8_8_primer_intervalo PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[z_critico-args0-1.645-0.0005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[z_critico-args1-1.96-0.0005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[z_critico-args2-2.33-0.005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[t_critico-args3-1.323-0.0005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[t_critico-args4-2.365-0.0005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[t_critico-args5-2.12-0.0005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[chi2_critico-args6-4.86518-1e-05] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[chi2_critico-args7-12.5916-0.0001] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[chi2_critico-args8-16.919-0.0005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[chi2_critico-args9-3.325-0.0005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[chi2_critico-args10-5.991-0.0005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[chi2_critico-args11-0.103-0.0005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[f_critico-args12-3.48-0.005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[f_critico-args13-2.88-0.005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[f_critico-args14-3.97-0.005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[f_critico-args15-5.29-0.005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[f_critico-args16-7.46-0.005] PASSED
tests/test_libro.py::test_valores_criticos_de_las_tablas[f_critico-args17-9.52-0.005] PASSED
tests/test_motor.py::test_momentos_de_las_poblaciones[normal] PASSED
tests/test_motor.py::test_momentos_de_las_poblaciones[uniforme] PASSED
tests/test_motor.py::test_momentos_de_las_poblaciones[exponencial] PASSED
tests/test_motor.py::test_momentos_de_las_poblaciones[gamma] PASSED
tests/test_motor.py::test_momentos_de_las_poblaciones[lognormal] PASSED
tests/test_motor.py::test_momentos_de_las_poblaciones[t] PASSED
tests/test_motor.py::test_momentos_de_las_poblaciones[dado] PASSED
tests/test_motor.py::test_momentos_de_las_poblaciones[bernoulli] PASSED
tests/test_motor.py::test_validacion_de_poblaciones PASSED
tests/test_motor.py::test_t_exacto_bajo_normalidad[2] PASSED
tests/test_motor.py::test_t_exacto_bajo_normalidad[5] PASSED
tests/test_motor.py::test_t_exacto_bajo_normalidad[30] PASSED
tests/test_motor.py::test_z_sigma_exacto_bajo_normalidad[1] PASSED
tests/test_motor.py::test_z_sigma_exacto_bajo_normalidad[4] PASSED
tests/test_motor.py::test_z_sigma_exacto_bajo_normalidad[50] PASSED
tests/test_motor.py::test_chi2_exacto_bajo_normalidad[3] PASSED
tests/test_motor.py::test_chi2_exacto_bajo_normalidad[10] PASSED
tests/test_motor.py::test_chi2_exacto_bajo_normalidad[100] PASSED
tests/test_motor.py::test_pivote_exponencial_exacto[1] PASSED
tests/test_motor.py::test_pivote_exponencial_exacto[5] PASSED
tests/test_motor.py::test_pivote_exponencial_exacto[40] PASSED
tests/test_motor.py::test_t_agrupada_exacta_con_varianzas_iguales PASSED
tests/test_motor.py::test_f_exacta_bajo_normalidad PASSED
tests/test_motor.py::test_limites_unilaterales[inferior] PASSED
tests/test_motor.py::test_limites_unilaterales[superior] PASSED
tests/test_motor.py::test_combinar_limites_da_1_menos_2alfa PASSED
tests/test_motor.py::test_z_con_s_coincide_con_formula_exacta_bajo_normalidad PASSED
tests/test_motor.py::test_wald_montecarlo_coincide_con_cobertura_exacta PASSED
tests/test_motor.py::test_wald_p_09_n_10_es_muy_malo PASSED
tests/test_motor.py::test_chi2_con_exponencial_converge_al_limite_equivocado PASSED
tests/test_motor.py::test_t_con_exponencial_se_recupera_con_n_grande PASSED
tests/test_motor.py::test_t_agrupada_falla_con_varianzas_y_tamanos_distintos PASSED
tests/test_motor.py::test_amplitud_z_sigma_es_deterministica PASSED
tests/test_motor.py::test_amplitud_media_frente_a_teoria[media_t] PASSED
tests/test_motor.py::test_amplitud_media_frente_a_teoria[varianza_chi2] PASSED
tests/test_motor.py::test_amplitud_cae_como_raiz_de_n PASSED
tests/test_motor.py::test_c4 PASSED
tests/test_motor.py::test_misma_semilla_mismo_resultado PASSED
tests/test_motor.py::test_semillas_distintas_resultados_distintos PASSED
tests/test_motor.py::test_resultado_no_depende_del_tamano_del_lote PASSED
tests/test_motor.py::test_muestra_individual_reproduce_el_intervalo PASSED
tests/test_motor.py::test_dos_muestras_independientes_y_reproducibles PASSED
tests/test_motor.py::test_una_muestra_de_100000 PASSED
tests/test_motor.py::test_cien_mil_muestras PASSED
tests/test_motor.py::test_muchas_muestras_grandes_con_memoria_acotada PASSED
tests/test_motor.py::test_trayectoria_coincide_con_calculo_directo PASSED
tests/test_motor.py::test_proporcion_usa_binomial_y_cuenta_bien_las_observaciones PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs0-\u2265 2] PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs1-m\xe1ximo] PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs2-B debe] PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs3-confianza] PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs4-Tipo] PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs5-no est\xe1 definido] PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs6-no est\xe1 definido] PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs7-dos poblaciones] PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs8-l\xedmite] PASSED
tests/test_motor.py::test_parametros_invalidos[kwargs9-desconocido] PASSED
tests/test_motor.py::test_varianza_infinita_bloquea_z_sigma PASSED
tests/test_motor.py::test_funciones_rechazan_argumentos_invalidos[z_critico-args0] PASSED
tests/test_motor.py::test_funciones_rechazan_argumentos_invalidos[z_critico-args1] PASSED
tests/test_motor.py::test_funciones_rechazan_argumentos_invalidos[t_critico-args2] PASSED
tests/test_motor.py::test_funciones_rechazan_argumentos_invalidos[media_t-args3] PASSED
tests/test_motor.py::test_funciones_rechazan_argumentos_invalidos[media_z_sigma-args4] PASSED
tests/test_motor.py::test_funciones_rechazan_argumentos_invalidos[varianza_chi2-args5] PASSED
tests/test_motor.py::test_funciones_rechazan_argumentos_invalidos[n_para_proporcion-args6] PASSED
tests/test_motor.py::test_cobertura_error_estandar_y_contraste PASSED
tests/test_paginas.py::test_paginas_estaticas[inicio.py] PASSED
tests/test_paginas.py::test_paginas_estaticas[fundamentos.py] PASSED
tests/test_paginas.py::test_paginas_estaticas[correspondencia.py] PASSED
tests/test_paginas.py::test_paginas_estaticas[calculadora.py] PASSED
tests/test_paginas.py::test_experimento_1_varios_procedimientos PASSED
tests/test_paginas.py::test_experimento_2 PASSED
tests/test_paginas.py::test_experimento_3 PASSED
tests/test_paginas.py::test_experimento_4 PASSED
tests/test_paginas.py::test_experimento_5[normal] PASSED
tests/test_paginas.py::test_experimento_5[exponencial] PASSED
tests/test_paginas.py::test_experimento_5[t] PASSED
tests/test_paginas.py::test_experimento_5[dado] PASSED
tests/test_paginas.py::test_experimento_6 PASSED
tests/test_paginas.py::test_calculadora_todos_los_ejemplos_y_procedimientos PASSED

============================= 117 passed =============================
```

## Comparación numérica con expresiones analíticas (muestra)

| Cantidad | Analítico | Aplicación / simulación |
|---|---|---|
| Ej. 8.11: IC 95 % para μ | 2959 ± 32.7 (libro) | [2926.32, 2991.68] → 2959 ± 32.68 |
| Ej. 8.12: IC 95 % para μ₁ − μ₂ | [−1.05, 8.37] (libro) | [−1.046, 8.379] |
| Ej. 8.13: IC 90 % para σ² | (3.53, 205.24) con χ².95 = .103 (libro) | (3.528, 206.07) con χ².95 = 0.10259 |
| Ej. 8.7: IC 90 % para μ | (29.71, 36.29) (libro) | (29.7103, 36.2897) |
| Ej. 8.8: IC 98 % para p₁ − p₂ | [−.1451, .2251] con z = 2.33 (libro) | [−.1449, .2249] con z = 2.3263 |
| Cobertura exacta de Wald, n = 35, p = .5 | 0.9590 (suma binomial) | Monte Carlo dentro de 4 e.e. |
| Cobertura de Z con S, normal, n = 5 | P(\|T₄\| ≤ 1.96) = 0.8784 | Monte Carlo dentro de 4 e.e. |
| Límite de cobertura χ², exponencial | 2Φ(0.98) − 1 = 0.673 | 0.687 con n = 1000 (B = 3000, valores por defecto del Exp. 6) |
| E(S)/σ con n = 5 | c₄(5) = 0.9400 | 0.940 (200 000 réplicas) |
