# Preguntas difíciles que podría hacer el profesor

Cada respuesta indica en qué parte del libro o de la aplicación se apoya.

---

### Sobre el concepto de confianza

**1. Ustedes obtuvieron el intervalo [−0.44, 0.25] para μ. ¿Cuál es la probabilidad de que μ esté ahí?**
Una vez observada la muestra, el intervalo es fijo y μ también: μ está o no está, así que la probabilidad es 0 o 1.
El 95 % describe el **procedimiento**: $P(\hat\theta_L\le\theta\le\hat\theta_U)=.95$ con los extremos aleatorios, antes
de observar la muestra (Sección 8.5, p. 406; p. 414–415: «uno tiene 95 % de confianza … ya que éste se obtuvo usando
un procedimiento que genera intervalos que contienen el parámetro aproximadamente 95 % de las veces»). El
Experimento 1 lo muestra: cada intervalo individual cubre o no cubre.

**2. ¿Qué es aleatorio en un intervalo de confianza?**
Los extremos $\hat\theta_L$ y $\hat\theta_U$, porque son estadísticos (Definición 7.1). θ es una constante desconocida.

**3. ¿Por qué el evento «θ ∈ IC» tiene la misma probabilidad que «−z ≤ Z ≤ z»?**
Porque es **el mismo evento** escrito de otra forma: se obtiene con operaciones que no cambian el conjunto de
resultados (multiplicar por una constante positiva, sumar una constante, multiplicar por −1 e invertir las
desigualdades; Sección 8.5, p. 407 y Ejemplo 8.6). En el Experimento 5, pestaña «Del capítulo 7 al 8», se comprueba
réplica por réplica.

### Sobre la simulación

**4. ¿Su simulación demuestra el Teorema 7.3?**
No. Un teorema vale para todo n y toda σ; la simulación ilustra un caso concreto con error de Monte Carlo. Lo que sí
puede hacer la simulación es **refutar**: si el intervalo χ² con población exponencial cubre 0.69 ± 0.017, queda
claro que no tiene coeficiente 95 % fuera de la normalidad.

**5. Su cobertura dio 0.9478 y no 0.95. ¿Está mal el programa?**
No necesariamente. $\hat c$ es una proporción de B ensayos de Bernoulli, con error estándar $\sqrt{c(1-c)/B}$
(Tabla 8.1). Con B = 10 000, $\sqrt{.95\cdot.05/10\,000}=0.0022$, así que 0.9478 está a una distancia de 1 error
estándar: compatible. La app calcula esa distancia y dice si supera 1.96.

**6. ¿Cuántas réplicas B necesitan para afirmar que la cobertura es 95 % con error menor que 0.001?**
Con la Sección 8.7 aplicada a $\hat c$: $B=1.96^2(.95)(.05)/.001^2\approx182\,476$.

**7. ¿Cuál es la diferencia entre una muestra de 100 000 y 100 000 muestras?**
n = 100 000 y B = 1 da **un** intervalo de amplitud ≈ $2z\sigma/\sqrt{10^5}$: alta precisión, pero contiene o no a θ.
B = 100 000 da cien mil intervalos, con los que se estima la cobertura (la fiabilidad del procedimiento). Pestaña
«Una sola muestra que crece» del Experimento 2.

**8. ¿Cómo garantizan que el programa no se bloquea con n = 100 000?**
Se generan lotes de a lo sumo 4 millones de números (≈ 32 MB) y solo se guardan media, varianza y suma de cada
muestra. 1000 muestras de 100 000 se procesan con unos 64 MB de pico. Hay además límites: n × B ≤ 3 × 10⁸.

**9. ¿Por qué en las proporciones no generan los ceros y unos?**
Porque $Y=\sum X_i$ con $X_i$ Bernoulli independientes tiene **exactamente** distribución Binomial(n, p) (Sección 7.5).
Generar Y directamente da la misma distribución del estadístico con un costo que no depende de n.

**10. ¿Cómo saben que el generador aleatorio y el código están bien?**
(a) La calculadora reproduce los ejemplos del libro con datos fijos. (b) Las coberturas simuladas de procedimientos
exactos dan 1 − α dentro de 4 errores estándar. (c) Para el intervalo de Wald, la cobertura simulada coincide con la
**cobertura exacta** calculada sin simular, sumando probabilidades binomiales. (d) Media y varianza de cada población
simulada coinciden con las fórmulas del capítulo 4. Son 117 pruebas automáticas.

### Sobre los procedimientos

**11. ¿Por qué usar t y no z si σ es desconocida?**
Porque $(\bar Y-\mu)/(S/\sqrt n)$ no es normal: es $t_{n-1}$ (Definición 7.2 con los Teoremas 7.1 y 7.3), con colas más
pesadas ($V(T)=\nu/(\nu-2)>1$). Con z y n pequeño se subcubre: con normalidad y n = 5 la cobertura real de
$\bar Y\pm1.96S/\sqrt n$ es $P(|T_4|\le1.96)=0.878$ (Experimento 3).

**12. ¿Cuándo dan lo mismo t y z?**
Cuando los grados de libertad son grandes: $t_{\alpha/2,\nu}\to z_{\alpha/2}$. El libro dice que «los intervalos son casi
equivalentes cuando los grados de libertad exceden de 30» (p. 430).

**13. ¿Por qué el intervalo t necesita que Ȳ y S² sean independientes?**
La Definición 7.2 exige que Z y W sean independientes. Esa independencia sale del Teorema 7.3 y solo vale bajo
normalidad. En el Experimento 5 se ve: correlación ≈ 0 con la normal y fuertemente positiva con la exponencial.

**14. ¿Por qué el intervalo para σ² no es simétrico alrededor de S²?**
Porque la χ² no es simétrica. El libro elige colas de igual área (Figura 8.11), no el intervalo más corto (p. 434).

**15. ¿Por qué el intervalo para σ² falla con la exponencial incluso con n = 1000, si el TCL dice que todo se vuelve
normal?**
El TCL hace que $(n-1)S^2/\sigma^2$ sea aproximadamente normal, pero con varianza $(n-1)(2+\kappa)$, donde κ es la
curtosis en exceso; el intervalo usa los cuantiles de una χ², que suponen varianza $2(n-1)$. Solo coinciden si κ = 0.
La cobertura converge a $2\Phi(z_{\alpha/2}\sqrt{2/(2+\kappa)})-1$, que vale 0.673 para la exponencial (κ = 6).
Es una derivación complementaria, coherente con la advertencia de la Sección 8.9.

**16. Entonces, ¿por qué la t sí se arregla con n grande y la χ² no?**
Para la t, el estadístico tiende a N(0,1) y los cuantiles $t_{\alpha/2,n-1}$ tienden a $z_{\alpha/2}$: el límite es el
correcto. Para la χ², el estadístico tiende a una normal con la varianza equivocada, y los cuantiles χ² se calibran
para otra varianza: el límite es incorrecto.

**17. ¿Qué pasa con el intervalo para p si p̂ = 0 o p̂ = 1?**
El error estándar estimado $\sqrt{\hat p\hat q/n}$ es 0 y el intervalo se reduce a un punto, que no contiene a p
(salvo que p sea 0 o 1). Con p = .9 y n = 10 pasa en el 35 % de las muestras: la cobertura exacta es 0.65. No invalida
el método: se usó fuera de su condición de muestra grande (regla p ± 3√(pq/n) ∈ (0, 1), Sección 7.5; Ejercicio 8.54).

**18. ¿Por qué la cobertura del intervalo para p oscila al variar p?**
Porque $\hat p$ es discreto (n + 1 valores). Al mover p, puntos $y$ entran y salen del conjunto de valores cuyo
intervalo contiene a p, y la suma de probabilidades salta.

**19. ¿Cuándo es peligroso usar la t con varianza agrupada?**
Cuando $\sigma_1^2\neq\sigma_2^2$ y $n_1\neq n_2$ (Sección 8.10). Si la muestra grande viene de la población menos
variable, $S_p^2$ subestima la variabilidad real: con $n_1=40$, $n_2=10$ y $\sigma_2/\sigma_1=4$ la cobertura simulada
fue 0.708. Con $n_1=n_2$ el intervalo es robusto.

**20. ¿Qué es exacto y qué es asintótico en su aplicación?**
Exactos bajo sus supuestos: Z con σ conocida y población normal, t, χ², t agrupada, F, pivote exponencial.
Asintóticos: Z con S, proporción, diferencia de medias y de proporciones con Z, y la Z con σ conocida sin normalidad.
La convergencia en distribución del TCL es un resultado sobre el límite: no dice qué tan buena es la aproximación con
n = 10. Por eso se simula.

**21. ¿Por qué S² divide por n − 1?**
Porque así es insesgado: $E[\sum(Y_i-\bar Y)^2]=(n-1)\sigma^2$ (Ejemplo 8.1), y esto vale para cualquier población.
Además, el pivote del Teorema 7.3 se escribe con $(n-1)S^2=\sum(Y_i-\bar Y)^2$. Insesgado no significa menor MSE:
bajo normalidad, $S'^2$ (que divide por n) tiene menor MSE (Experimento 5, pestaña «Sesgo y MSE»).

**22. ¿S es un estimador insesgado de σ?**
No. Bajo normalidad, $E(S)=\sigma c_4(n)<\sigma$ (por ejemplo, $c_4(5)=0.940$). Es la desigualdad de Jensen: la raíz
cuadrada es cóncava. Este resultado se usa en la amplitud teórica del intervalo t.

### Sobre el nivel de confianza y el tamaño muestral

**23. ¿Por qué no usar siempre 99.9 %?**
Porque el valor crítico crece sin cota cuando 1 − α → 1, y con él la amplitud. Con n fijo, confianza y precisión
compiten. Con las mismas muestras, el cociente de amplitudes 99 %/95 % es $z_{.005}/z_{.025}=1.314$ (Experimento 4).

**24. Si duplico n, ¿la amplitud se reduce a la mitad?**
No: se divide por √2 ≈ 1.41. Para reducirla a la mitad hay que cuadruplicar n (Sección 8.7). La pendiente simulada en
log-log fue −0.511.

**25. ¿Cómo calculan el n necesario?**
Igualando $z_{\alpha/2}\sigma_{\hat\theta}=B$ (Sección 8.7). Para p sin información previa se usa p = .5, que maximiza
pq (Ejemplo 8.9: n = 423).

### Sobre el libro

**26. ¿Por qué el libro dice en el Ejemplo 8.7 «aproximadamente 95 %»?**
Es una errata: el intervalo usa $z_{.05}=1.645$, es decir, 90 %. El propio párrafo dice antes «aproximadamente 90 %
de todos los intervalos».

**27. ¿Por qué sus resultados no coinciden exactamente con los del libro en el Ejemplo 8.13?**
El libro usa $\chi^2_{.95,2}=.103$ (tabla), y el valor exacto es 0.1026. Por eso su límite superior es 205.24 y el de la
app 206.07. La página «Valores críticos frente a las tablas» muestra todas estas diferencias de redondeo.
