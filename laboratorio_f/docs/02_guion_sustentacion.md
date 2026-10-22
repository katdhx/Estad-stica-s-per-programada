# Guion de sustentación: Laboratorio F

Duración sugerida: 12 a 15 minutos. Dos expositores (A y B). Lo que va entre corchetes es lo que se hace en la
aplicación. Antes de entrar: abrir la aplicación y dejarla en **Inicio** con la forma **Normal** y n = 10.

---

## 1. Planteamiento (A, 1 min) — página Inicio

«En los capítulos 7 y 8 la distribución F sirve para comparar dos varianzas. El libro la usa en el Ejemplo 7.7, en
el Ejercicio 7.27 y en el intervalo para σ₂²/σ₁² del Ejercicio 8.125. Todo eso tiene una condición: que las dos
poblaciones sean normales. Nuestra pregunta es qué pasa cuando no lo son.»

«Para responderla no basta con el teorema, porque el teorema solo habla del caso normal. Lo que hacemos es simular:
generamos miles de pares de muestras y medimos si la F acierta.»

## 2. La cadena del libro (A, 2 min) — Inicio

[Señalar las cuatro tarjetas.]

«La F sale de una cadena de cuatro pasos. Primero, la normalidad. Segundo, el Teorema 7.3: (n−1)S²/σ² es una
chi-cuadrado con n−1 grados de libertad. Tercero, la Definición 7.3: el cociente de dos chi-cuadrado independientes,
cada una dividida por sus grados de libertad, es una F. Cuarto, lo que promete la F: por ejemplo, que el intervalo
del 95 % acierta el 95 % de las veces.»

[Con Normal: señalar el histograma sobre la curva y el 95 %.]

«Aquí las dos poblaciones son normales. Simulamos 20 000 pares de muestras de tamaño 10 y calculamos F* para cada
uno. El histograma cae sobre la curva F(9, 9) del libro, y el 95 % de los intervalos contiene el valor verdadero.
Esto no es una aproximación: con normalidad el resultado es exacto para cualquier n.»

[Cambiar a Exponencial.]

«Ahora las dos poblaciones son exponenciales. Fíjense en la cadena: el primer eslabón se pone en rojo, y con él
todos los demás. El histograma ya no sigue la curva y la cobertura cae a cerca del 77 %. El intervalo que dice
"95 %" acierta tres de cada cuatro veces.»

[Mover n a 100.]

«Y lo más importante: si aumentamos n a 100, no mejora. Empeora. Eso es lo que vamos a explicar.»

## 3. Dónde se rompe (B, 2.5 min) — Experimento 2

[Abrir «Dónde se rompe la cadena» con la t de 5 gl. Ejecutar.]

«Revisamos la cadena eslabón por eslabón con las mismas muestras.»

«Eslabón 1: el promedio de S²/σ² da prácticamente 1. S² es insesgado para cualquier población; lo dice el
Ejemplo 8.1. El problema no está en el centro.»

«Eslabón 2: la varianza de S². Si W fuera chi-cuadrado, la varianza de S²/σ² sería 2/(n−1). La simulación da
casi cuatro veces más. Aquí se rompe. Hay una fórmula general, que no está en el libro pero se deduce con los
valores esperados del capítulo 5: V(S²) = σ⁴[2/(n−1) + κ/n], donde κ es la curtosis en exceso, que mide qué tan
pesadas son las colas. Con la normal κ = 0 y se recupera lo del Teorema 7.3.»

«Eslabón 3: el histograma de W ya no es una chi-cuadrado; tiene la misma media pero es más ancho.»

«Eslabón 4: la independencia de la Definición 7.3 sí se cumple siempre, porque las muestras son independientes.
Lo que falla es que W₁ y W₂ no son chi-cuadrado, y la F lo hereda.»

## 4. Las promesas del libro (B, 1.5 min) — Experimento 3

[Abrir «¿Se cumple lo que promete la F?» con la exponencial. Ejecutar.]

«Este es el Ejemplo 7.7 tal como está en el libro: n₁ = 6, n₂ = 10, varianzas iguales. La F dice que el cociente de
las varianzas muestrales pasa de 3.48 el 5 % de las veces. Con poblaciones exponenciales pasa el 14 %, casi tres
veces más. Las probabilidades del Ejercicio 7.27 también fallan.»

[Pestaña «¿Mejora con más datos?», calcular.]

«Con la normal la línea se queda en 5 % para todo n. Con la exponencial sube y se estanca cerca del 20 %.»

## 5. El intervalo del capítulo 8 (A, 2 min) — Experimento 4

[Abrir «El intervalo para σ₂²/σ₁²». Con normales, ejecutar.]

«Cada línea es un intervalo del Ejercicio 8.125 construido con una réplica. Los naranjas no contienen el valor
verdadero. Con normales, la cobertura es 95 % dentro del error de simulación.»

[Pestaña «Por qué es el mismo problema que la F».]

«El intervalo se obtiene despejando σ₂²/σ₁² de F₁₋α/₂ ≤ F* ≤ F_α/₂. Despejar no cambia el evento. Por eso la
cobertura del intervalo es exactamente la probabilidad de que F* caiga en el centro de la F. Si F* no es F, la
cobertura no es 1 − α. El libro advierte lo mismo en la Sección 8.9 para el intervalo de una varianza.»

[Pestaña «¿Mejora con más datos?», calcular con exponencial y normal.]

«Con la exponencial la cobertura baja de cerca de 83 % con n = 5 hasta estancarse alrededor de 67 %. La línea discontinua es
el límite teórico, 2Φ(z·√(2/(2+κ))) − 1. Por qué no mejora: los dos términos de V(S²) bajan al mismo ritmo, así que
la proporción entre lo real y lo supuesto no cambia con n. Con la media el TCL nos rescata; con la varianza, no.»

## 6. El patrón general (B, 2 min) — Experimento 5

[Abrir «Mapa de robustez». Simular las distribuciones.]

«Probamos catorce distribuciones: simétricas, asimétricas, de colas livianas y pesadas. Las ordenamos por su
curtosis y caen sobre una sola curva. La normal es el único punto exactamente en 95 %. A la izquierda, la uniforme
cubre de más; a la derecha, las de colas pesadas cubren cada vez menos.»

«Lo que decide el error no es la asimetría, son las colas. La t con 7 grados de libertad es simétrica y la gamma
con α = 3 es asimétrica, pero las dos tienen κ = 2 y fallan casi igual.»

[Pestaña «Parejas de formas».]

«Basta con que una de las dos poblaciones tenga colas pesadas para que la cobertura caiga.»

## 7. Cierre (A, 1 min)

«Conclusiones:

1. Bajo normalidad, el Teorema 7.3 y la Definición 7.3 hacen que la F sea exacta para cualquier n; la simulación
   lo confirma.
2. Sin normalidad, el eslabón que falla es el Teorema 7.3: S² sigue siendo insesgado, pero varía distinto de lo
   que supone la chi-cuadrado.
3. El error lo decide la curtosis de la población. Colas pesadas: los intervalos fallan de más; colas livianas:
   aciertan de más.
4. Aumentar n no lo arregla. A diferencia de los intervalos para la media, aquí no hay Teorema Central del Límite
   que rescate el procedimiento.

En la práctica, antes de usar la F para comparar varianzas hay que preguntarse por las colas de los datos.»

---

## Plan B si algo falla

- Si la aplicación se cierra: volver a abrir `iniciar_windows.bat` (tarda 5 segundos).
- Si una simulación tarda: bajar B en la barra lateral (10 000 es suficiente para mostrar el efecto).
- Las cifras de este guion están en la sección 7 del documento matemático por si hay que citarlas sin la aplicación.
