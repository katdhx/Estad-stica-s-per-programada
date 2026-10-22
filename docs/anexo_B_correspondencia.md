# Anexo B. Tabla de correspondencia con el libro

Generado desde `lab/correspondencia.py`. Las páginas son las del libro impreso (en el PDF hay que sumar 24).

## Módulos de la aplicación

| Módulo | Archivo | Resultado del libro | Sección | Página | Qué se comprueba |
|---|---|---|---|---|---|
| Inicio: Figura 8.8 en vivo | `paginas/inicio.py` | Figura 8.8; intervalo para p | 8.6 | 414 | 24 intervalos del 95 % con n = 35 y p = .5; ¿cuántos contienen p? |
| Fundamentos | `paginas/fundamentos.py` | Def. 7.1–7.3; Teo. 7.1–7.5; Def. 8.1–8.5; Tabla 8.1 | 7.1–7.5; 8.1–8.10 | 346–437 | Enunciados y deducciones. |
| Exp. 1: construcción | `paginas/exp1_construccion.py` | Coeficiente de confianza; método del pivote; Ejemplo 8.6 | 8.5, 8.6 | 406–415 | Cada muestra produce un intervalo; fracción que cubre; F ~ Binomial(B, α). |
| Exp. 2: tamaño muestral | `paginas/exp2_tamano.py` | Teo. 7.1; Tabla 8.1 (σ/√n); selección de n; Ej. 8.9–8.10 | 7.2, 8.3, 8.7 | 353, 397, 421–424 | Amplitud ∝ n^(−1/2); una muestra de 10⁵ frente a 10⁵ muestras. |
| Exp. 3: cobertura | `paginas/exp3_cobertura.py` | Coeficiente de confianza; error estándar de p̂ (Tabla 8.1) | 8.5, 8.6 | 406, 397, 414–417 | ĉ frente a 1 − α; error de Monte Carlo √(c(1−c)/B); comparación de procedimientos. |
| Exp. 4: nivel de confianza | `paginas/exp4_nivel.py` | Valores críticos z_{α/2}, t_{α/2}; Figuras 8.7, 8.10, 8.11 | 8.6, 8.8, 8.9 | 411, 426, 435 | Mismas muestras al 90/95/99 %; razón de amplitudes z_.005/z_.025. |
| Exp. 5: media muestral | `paginas/exp5_distribuciones.py` | Teorema 7.1; Teorema 7.4 (TCL); Tabla 7.1; Figuras 7.5–7.7 | 7.2, 7.3 | 353, 370–372 | Histograma de Ȳ frente a N(μ, σ²/n). |
| Exp. 5: varianza muestral | `paginas/exp5_distribuciones.py` | Teorema 7.3 | 7.2 | 357 | (n−1)S²/σ² frente a χ²(n−1); se rompe sin normalidad. |
| Exp. 5: t de Student | `paginas/exp5_distribuciones.py` | Definición 7.2; Figura 7.3 | 7.2 | 360 | T = √n(Ȳ−μ)/S frente a t(n−1) y N(0, 1). |
| Exp. 5: independencia | `paginas/exp5_distribuciones.py` | Teorema 7.3 (Ȳ y S² independientes) | 7.2 | 357 | Correlación Ȳ–S² bajo normalidad y fuera de ella. |
| Exp. 5: del cap. 7 al 8 | `paginas/exp5_distribuciones.py` | Método del pivote | 8.5, 8.8 | 407, 426 | |T| ≤ t_{α/2} es el mismo evento que μ ∈ IC. |
| Exp. 5: sesgo y MSE | `paginas/exp5_distribuciones.py` | Ejemplo 8.1; Definiciones 8.2–8.4 | 8.2, 8.3 | 393, 398 | E(S²) = σ²; E(S′²) = (n−1)σ²/n; MSE = V + B². |
| Exp. 5: binomial | `paginas/exp5_distribuciones.py` | Aproximación normal a la binomial; Ejemplo 7.11 | 7.5 | 378–382 | Corrección por continuidad; regla p ± 3√(pq/n). |
| Exp. 6: χ² sin normalidad | `paginas/exp6_supuestos.py` | Intervalo para σ²; advertencia de robustez | 8.9, 8.10 | 434–437 | Cobertura con poblaciones no normales; no se corrige con n. |
| Exp. 6: t sin normalidad | `paginas/exp6_supuestos.py` | Robustez del intervalo t | 8.8, 8.10 | 425, 437 | La cobertura converge a la nominal (TCL). |
| Exp. 6: proporción extrema | `paginas/exp6_supuestos.py` | Regla p ± 3√(pq/n); Ejercicios 8.54–8.55 | 7.5, 8.6 | 380, 417 | Cobertura exacta del intervalo de Wald; p̂ ∈ {0, 1}. |
| Exp. 6: t agrupada | `paginas/exp6_supuestos.py` | Supuesto σ₁² = σ₂²; robustez si n₁ ≈ n₂ | 8.8, 8.10 | 427–430, 437 | Cobertura con varianzas distintas y n₁ ≠ n₂. |
| Calculadora: ejemplos | `paginas/calculadora.py` | Ejemplos 8.4, 8.7, 8.8, 8.11, 8.12, 8.13 | 8.5–8.9 | 407–435 | Reproduce los resultados impresos. |
| Calculadora: tablas | `paginas/calculadora.py` | Valores críticos de las Tablas 4–7 citados en el texto | 7.2 | 356–363 | SciPy frente a tablas. |
| Motor: fórmulas | `lab/intervalos.py` | Fórmulas de los intervalos | 8.6, 8.8, 8.9 | 411–435 | Funciones puras vectorizadas. |
| Motor: fichas | `lab/procedimientos.py` | Parámetro, estimador, pivote, supuestos y referencias | 7.2–8.9 | — | Ficha matemática de cada procedimiento. |
| Motor: poblaciones | `lab/poblaciones.py` | Distribuciones normal, uniforme, gamma, log-normal, t, dado | 4.4–4.6; Ej. 4.182–4.183; Def. 7.2; Ej. 7.1 | — | Media y varianza de cada población. |
| Motor: simulación | `lab/motor.py` | Muestreo repetido (Def. 7.1; Sec. 8.5) | 7.1, 8.5 | 347, 406 | Monte Carlo por lotes, reproducible. |
| Motor: teoría | `lab/teoria.py` | Valores esperados de amplitudes, coberturas exactas | 7.2, 8.6 | — | Comparación empírica frente a teórica (resultados marcados como complementarios). |

## Procedimientos de intervalos de confianza

| Procedimiento | Sección | Ejemplos | Se apoya en | Tipo |
|---|---|---|---|---|
| μ, σ conocida (Z) | 8.6 (Ej. 8.6) | Ej. 7.2, 7.3 | Teo. 7.1 / Teo. 7.4 | Exacto si normal; asintótico si no |
| μ, muestra grande con S (Z) | 8.6 | Ej. 8.7 | Teo. 7.4 + sustitución σ → S | Asintótico |
| μ, t de Student | 8.8 | Ej. 8.11 | Teo. 7.1, 7.3, Def. 7.2 | Exacto bajo normalidad |
| σ², χ² | 8.9 | Ej. 8.13; Ej. 7.5 | Teo. 7.3 | Exacto bajo normalidad |
| p, muestra grande | 8.6 | Ej. 8.2; Fig. 8.8 | Sec. 7.5 (TCL) | Asintótico |
| μ₁ − μ₂, muestras grandes (Z) | 8.6 | Ej. 8.3 | Tabla 8.1 | Asintótico |
| μ₁ − μ₂, t agrupada | 8.8 | Ej. 8.12 | Teo. 7.2, 7.3, Def. 7.2 | Exacto bajo normalidad y σ₁ = σ₂ |
| p₁ − p₂ | 8.6 | Ej. 8.8 | Tabla 8.1 | Asintótico |
| θ exponencial, 2ΣY/θ | 8.5 (ejercicio) | Ej. 8.4; Ejercicios 8.46–8.47 | FGM (Sec. 6.5) | Exacto |
| σ₂²/σ₁², F | Ejercicio 8.125 | — | Def. 7.3 | Exacto bajo normalidad |
