# Guion de sustentación

**Duración objetivo:** 15–18 minutos de exposición, más preguntas.
**Formato:** dos personas (Karol y Juan) que se turnan; cada bloque indica quién habla, qué se muestra en pantalla y
qué se dice. Los números entre corchetes salen de las configuraciones por defecto con semilla 2026. Si cambian un
control, cambian los números: digan lo que **ven**, no lo que dice este guion.

**Antes de entrar:** abrir la aplicación, cargar Inicio y comprobar que el botón «Ejecutar simulación» responde.
Tener el libro abierto en la p. 414 (Figura 8.8).

---

## Bloque 1. Qué es un intervalo de confianza (2 min). Habla: Karol

**Pantalla:** Inicio, «La Figura 8.8, en vivo».

> «Este laboratorio parte de la Figura 8.8 del libro, en la página 414. Allí se simulan 24 experimentos binomiales con
> n = 35 y p = 0.5. Cada uno da un intervalo p̂ ± 1.96·√(p̂q̂/35), y 23 de los 24 contienen a p. Aquí reproducimos esa
> figura. [Tanda 1: 23 de 24.] Pulsamos «Generar otra tanda»: cambian los intervalos, pero p sigue en 0.5. Lo aleatorio
> son los extremos del intervalo, no el parámetro.»

**Pantalla:** bajar a «Dos números que no hay que confundir».

> «Hay dos tamaños distintos. n es el tamaño de cada muestra y controla la **precisión** de un intervalo. B es cuántas
> veces repetimos el experimento y sirve para medir la **fiabilidad** del procedimiento. Una muestra de 100 000
> observaciones da un solo intervalo, muy angosto, que contiene o no a θ. Cien mil muestras dan cien mil intervalos,
> con los que estimamos la cobertura.»

## Bloque 2. De dónde salen las fórmulas (3 min). Habla: Juan

**Pantalla:** Fundamentos → «Método del pivote».

> «Todos los intervalos del capítulo 8 se obtienen con el método del pivote de la Sección 8.5. Un pivote es una función
> de la muestra y del parámetro cuya distribución no depende del parámetro. Con la Z del Ejemplo 8.6 los pasos son:
> enunciado de probabilidad, multiplicar por el error estándar, restar θ̂, multiplicar por −1. El evento no cambia, solo
> se reescribe, por eso conserva la probabilidad 1 − α.»

**Pantalla:** pestaña «Capítulo 7».

> «Los pivotes salen del capítulo 7. Teorema 7.1: si la población es normal, Ȳ es normal con varianza σ²/n. Teorema 7.3:
> (n−1)S²/σ² es chi-cuadrado con n−1 gl, y Ȳ y S² son independientes. Definición 7.2: con eso, (Ȳ−μ)/(S/√n) es una t con
> n−1 gl. Y el TCL, Teorema 7.4, dice qué pasa sin normalidad: la distribución de (Ȳ−μ)/(σ/√n) tiende a la normal
> estándar. Ojo: tiende, en el límite; no dice que sea normal para un n dado.»

**Pantalla:** Fichas → abrir «Media μ con σ desconocida (t)».

> «Cada procedimiento tiene una ficha con parámetro, estimador, distribución muestral, pivote, fórmula, supuestos,
> justificación, interpretación y la referencia exacta del libro.»

## Bloque 3. Experimento 1: qué significa 95 % (2 min). Habla: Karol

**Pantalla:** Experimento 1, valores por defecto (t, normal, n = 20, B = 100). Ejecutar.

> «Generamos 100 muestras normales de tamaño 20 y construimos el intervalo t para cada una. [95 de 100 contienen μ.]
> Los naranjas son los que fallan.» Escribir un número de muestra en «Inspeccionar»: «Aquí está la cuenta completa de
> esta muestra: ȳ, s, el valor t_{0.025,19} = 2.093 y el intervalo. La app recalcula ȳ con los datos crudos para
> comprobar que la cuenta es la misma.»

**Pantalla:** pestaña «Fundamentación matemática».

> «El número de intervalos que fallan es binomial(B, α): se esperaban 5 y hubo [5]. En el libro se esperaban 1.2 de 24
> y hubo 1.»

## Bloque 4. Experimento 2: tamaño muestral (2.5 min). Habla: Juan

**Pantalla:** Experimento 2 por defecto (t, exponencial θ = 10, n de 5 a 100 000, B = 400). Ejecutar.

> «La amplitud cae en escala log-log con pendiente [−0.511], y la teoría da −1/2. Toda amplitud es valor crítico por
> error estándar, y el error estándar de la Tabla 8.1 es σ/√n. Para dividir la amplitud por 10 hay que multiplicar n
> por 100: de [21.3] con n = 5 pasamos a [0.12] con n = 100 000.»

> «En la gráfica de cobertura: con n = 5 o 10 la t subcubre [≈ 86–87 %], porque la exponencial no es normal; al crecer
> n se acerca a 95 %. El intervalo se hace más estrecho pero no menos fiable.»

**Pantalla:** pestaña «Una sola muestra que crece».

> «Esto es una sola muestra de 100 000 observaciones: el intervalo se estrecha alrededor de θ, pero es una sola
> realización. Con esto no se puede decir nada sobre la cobertura.»

## Bloque 5. Experimento 3: cobertura y error de Monte Carlo (3 min). Habla: Karol

**Pantalla:** Experimento 3 por defecto (exponencial, n = 10, B = 10 000, comparar con Z con σ, Z con S y pivote).

> «La cobertura empírica es una proporción de B ensayos de Bernoulli, así que su error estándar es √(ĉ(1−ĉ)/B), la
> fórmula de la Tabla 8.1. Con B = 10 000 es [0.003].»

> «Con las mismas 10 000 muestras: el pivote exacto 2ΣY/θ, que es χ²(2n) (Ejemplo 8.4 y Ejercicio 8.47), da [0.949],
> compatible con 95 %. La t da [0.899] y la Z con S, [0.870]: la distancia es de más de 20 errores estándar, así que
> no es azar, es que con población asimétrica y n = 10 esos procedimientos no tienen coeficiente 95 %.»

**Pantalla:** pestaña «¿Por qué no da exactamente 1 − α?».

> «Hay cuatro razones: error de Monte Carlo, procedimiento asintótico, supuestos violados y discreción en
> proporciones. Solo la primera desaparece aumentando B.»

## Bloque 6. Experimento 4: nivel de confianza (1.5 min). Habla: Juan

**Pantalla:** Experimento 4 por defecto (t, normal, n = 25, 90/95/99 %). Ejecutar.

> «Mismas muestras, tres niveles. Los intervalos están anidados. Solo cambia el valor crítico, así que el cociente de
> amplitudes no depende de los datos: con z sería 2.576/1.960 = 1.314. Más confianza cuesta amplitud, y cuando el nivel
> tiende a 100 % la amplitud tiende a infinito. La única forma de ganar en las dos cosas es aumentar n.»

## Bloque 7. Experimento 5: el puente entre capítulos (2 min). Habla: Karol

**Pantalla:** Experimento 5, población exponencial, n = 5. Generar.

> «El histograma de Ȳ con n = 5 todavía es asimétrico [asimetría 0.90, teórica 2/√5 = 0.89]: la normal del TCL es solo
> aproximada. La curva naranja es la densidad exacta, una gamma.»

**Pantalla:** pestaña «Independencia de Ȳ y S²».

> «Bajo normalidad, Ȳ y S² son independientes (Teorema 7.3). Con la exponencial están fuertemente correlacionados, y por
> eso la t falla con n pequeño: la Definición 7.2 exige esa independencia.»

**Pantalla:** pestaña «Del capítulo 7 al 8».

> «La fracción de réplicas con |T| ≤ t_{α/2} es exactamente la fracción de intervalos que contienen μ, réplica a réplica.
> La cobertura del capítulo 8 es un área bajo la distribución muestral del capítulo 7.»

## Bloque 8. Experimento 6: supuestos (2.5 min). Habla: Juan

**Pantalla:** «χ² para σ² sin normalidad». Simular.

> «La Sección 8.9 dice que el intervalo para σ² es muy sensible a la normalidad. Lo medimos: con la normal da 95 %;
> con la exponencial [0.76 con n = 10, 0.69 con n = 1000]. Empeora con n y converge a un valor equivocado. La razón: el
> Teorema 7.3 necesita normalidad y no hay TCL que lo arregle; la varianza real de (n−1)S²/σ² depende de la curtosis.»

**Pantalla:** «t para μ sin normalidad». Simular.

> «En cambio, la t sí se recupera: con la exponencial pasa de [0.88 con n = 5] a [0.947 con n = 300]. Esa es la
> diferencia entre robusto y no robusto.»

**Pantalla:** «Proporción cerca de 0 o 1».

> «La cobertura exacta del intervalo para p se calcula sumando probabilidades binomiales. Oscila y se hunde cerca de 0
> y 1. Con p = 0.9 y n = 10 es [0.65]: en 35 % de las muestras p̂ = 1 y el intervalo es un punto. Los puntos de Monte
> Carlo caen sobre la curva exacta, lo que valida el motor.»

## Bloque 9. Validación y cierre (1 min). Habla: Karol

**Pantalla:** Calculadora → Ejemplo 8.11, y luego «Valores críticos frente a las tablas».

> «Para confiar en el programa, las 117 pruebas automáticas reproducen los ejemplos del libro: 8.11 da 2959 ± 32.7,
> igual que en la página 426; los valores críticos coinciden con las Tablas 4 a 7. Encontramos además una errata: el
> Ejemplo 8.7 es un intervalo del 90 %, pero el texto termina diciendo 95 %.»

> «En resumen: los teoremas del capítulo 7 dan los pivotes; el método del pivote da los intervalos; la simulación
> comprueba, para casos concretos, que la cobertura es la prometida cuando se cumplen los supuestos, y mide cuánto
> falla cuando no.»

---

## Plan B si algo falla

- Si la aplicación se congela con una simulación grande: reducir B. Los resultados ya calculados están en caché.
- Si no abre: `iniciar_windows.bat`, o en Anaconda Prompt `streamlit run app.py`.
- Llevar capturas o los HTML descargados de las gráficas clave por si el computador del salón falla.
