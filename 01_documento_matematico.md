# Laboratorio de intervalos de confianza: documento matemático

**Curso:** MATE 2509 Probabilidad y Estadística, Universidad de los Andes.
**Referencia principal:** Wackerly, D. D., Mendenhall, W. y Scheaffer, R. L., *Estadística matemática con aplicaciones*,
7.ª edición, Cengage, capítulos 7 y 8. Las páginas citadas son las del libro impreso; en el PDF hay que sumar 24.

Este documento explica qué hace la aplicación y **por qué**, con la matemática del libro. Los resultados que el
laboratorio añade por su cuenta, derivados con herramientas del curso pero que no aparecen en los capítulos 7 y 8,
están marcados como **[complementario]**.

---

## 0. Notación

| Símbolo | Significado |
|---|---|
| $Y_1,\dots,Y_n$ | Muestra aleatoria: variables independientes con la misma distribución (i.i.d.). |
| $n$ | Tamaño de **cada** muestra. |
| $B$ | Número de muestras independientes que genera la simulación (réplicas). |
| $\mu=E(Y_i)$, $\sigma^2=V(Y_i)$ | Media y varianza poblacionales. |
| $\bar Y=\frac1n\sum Y_i$ | Media muestral. |
| $S^2=\frac{1}{n-1}\sum(Y_i-\bar Y)^2$ | Varianza muestral (insesgada, Ejemplo 8.1). |
| $\theta$, $\hat\theta$ | Parámetro objetivo y su estimador. |
| $\sigma_{\hat\theta}$ | Error estándar de $\hat\theta$, es decir, su desviación estándar (Sección 8.3). |
| $1-\alpha$ | Coeficiente (nivel) de confianza. |
| $z_a,\ t_a,\ \chi^2_a,\ F_a$ | Valores con área $a$ en la cola **superior** (convención de las Tablas 4–7 del Apéndice 3). |
| $\hat c$ | Cobertura empírica: fracción de los $B$ intervalos que contienen a $\theta$. |

Una consecuencia de la convención de cola superior: $\chi^2_{1-\alpha/2}$ es el cuantil **pequeño** y $\chi^2_{\alpha/2}$ el grande.

---

## 1. Demostración y simulación

Un **teorema** (por ejemplo, el Teorema 7.3) afirma algo para **todo** $n$ y para **toda** muestra posible; se
justifica con un argumento lógico. Una **simulación de Monte Carlo** genera muchas muestras con el computador y
mide con qué frecuencia ocurre algo. Sus diferencias:

1. La simulación **no demuestra**: solo ilustra el resultado para los valores concretos de $n$, $\sigma$, la población
   y la semilla que se eligieron.
2. La simulación tiene **error medible**. La cobertura empírica $\hat c$ es una proporción muestral, con error estándar
   $\sqrt{c(1-c)/B}$ (Tabla 8.1).
3. La simulación **sí puede refutar**. Si el intervalo χ² con población exponencial cubre 69 % con un error estándar
   de 0.8 %, eso basta para concluir que su coeficiente no es 95 % fuera de la normalidad, justo lo que advierte la
   Sección 8.9.

La aplicación conecta siempre cada resultado empírico con el resultado teórico que debería observarse, y dice si la
diferencia se explica por el error de Monte Carlo.

---

## 2. Etapa 1: los resultados del libro que sostienen el programa

### 2.1 Capítulo 7: distribuciones muestrales

**Definición 7.1 (p. 347).** Un *estadístico* es una función de las variables observables de la muestra y de
constantes conocidas. Como es variable aleatoria, tiene distribución de probabilidad: su *distribución muestral*.
El libro la describe como «un modelo teórico para el histograma de frecuencia relativa de los posibles valores del
estadístico que observaríamos por medio de muestreo repetido». **Ese histograma es exactamente lo que construye la
simulación.**

**Teorema 7.1 (p. 353).** Si $Y_i\sim N(\mu,\sigma^2)$ son i.i.d., entonces $\bar Y\sim N(\mu,\sigma^2/n)$, y por tanto
$$Z=\frac{\bar Y-\mu}{\sigma/\sqrt n}\sim N(0,1).$$
Demostración: $\bar Y=\sum a_iY_i$ con $a_i=1/n$ es una combinación lineal de normales independientes; el Teorema 6.3
dice que es normal, con media $\sum a_i\mu=\mu$ y varianza $\sum a_i^2\sigma^2=\sigma^2/n$. **Es exacto para todo $n$.**

**Teorema 7.2 (p. 356).** $\sum_{i=1}^n\big((Y_i-\mu)/\sigma\big)^2\sim\chi^2_n$.

**Teorema 7.3 (p. 357).** Bajo normalidad,
$$W=\frac{(n-1)S^2}{\sigma^2}\sim\chi^2_{n-1},\qquad\text{y } \bar Y,\ S^2 \text{ son independientes.}$$
El libro demuestra el caso $n=2$ y remite al Ejercicio 13.93 para el caso general.

**Definición 7.2 (p. 360).** Si $Z\sim N(0,1)$ y $W\sim\chi^2_\nu$ son independientes, $T=Z/\sqrt{W/\nu}\sim t_\nu$.
Con los Teoremas 7.1 y 7.3:
$$T=\frac{\sqrt n(\bar Y-\mu)/\sigma}{\sqrt{\big[(n-1)S^2/\sigma^2\big]/(n-1)}}=\frac{\bar Y-\mu}{S/\sqrt n}\sim t_{n-1}.$$
Propiedades: simétrica, $E(T)=0$ si $\nu>1$, $V(T)=\nu/(\nu-2)>1$ si $\nu>2$, con colas más pesadas que la normal (Figura 7.3).

**Definición 7.3 (p. 362).** $F=(W_1/\nu_1)/(W_2/\nu_2)\sim F_{\nu_1,\nu_2}$, de donde $\dfrac{S_1^2/\sigma_1^2}{S_2^2/\sigma_2^2}\sim F_{n_1-1,n_2-1}$.

**Teorema 7.4, TCL (p. 372).** Si las $Y_i$ son i.i.d. con $E(Y_i)=\mu$ y $V(Y_i)=\sigma^2<\infty$, y
$U_n=(\bar Y-\mu)/(\sigma/\sqrt n)$, entonces $\lim_{n\to\infty}P(U_n\le u)=\Phi(u)$ para todo $u$. El libro sugiere
que $n>30$ suele bastar. La demostración opcional (Sección 7.4, Teorema 7.5) usa FGM: $m_{U_n}(t)\to e^{t^2/2}$.

**Sección 7.5 (p. 378).** Con $Y=\sum X_i$, $X_i\in\{0,1\}$, el TCL da $\hat p=Y/n\ \dot\sim\ N(p,pq/n)$. Regla práctica:
$p\pm3\sqrt{pq/n}\in(0,1)$ (o $n>9\cdot\frac{\max(p,q)}{\min(p,q)}$). Corrección por continuidad: Ejemplo 7.11.

### 2.2 Capítulo 8: estimación

- **Definiciones 8.2–8.4 (p. 393).** Insesgamiento $E(\hat\theta)=\theta$; sesgo $B(\hat\theta)=E(\hat\theta)-\theta$;
  $\mathrm{MSE}(\hat\theta)=E[(\hat\theta-\theta)^2]=V(\hat\theta)+B(\hat\theta)^2$.
- **Tabla 8.1 (p. 397).** Errores estándar de $\bar Y$ ($\sigma/\sqrt n$), $\hat p$ ($\sqrt{pq/n}$),
  $\bar Y_1-\bar Y_2$ ($\sqrt{\sigma_1^2/n_1+\sigma_2^2/n_2}$) y $\hat p_1-\hat p_2$ ($\sqrt{p_1q_1/n_1+p_2q_2/n_2}$).
- **Ejemplo 8.1 (p. 398).** $E(S^2)=\sigma^2$, mientras que $E(S'^2)=\frac{n-1}{n}\sigma^2$ si $S'^2$ divide por $n$.
  Vale para cualquier población con varianza finita.
- **Sección 8.5 (p. 406–407).** Si $P(\hat\theta_L\le\theta\le\hat\theta_U)=1-\alpha$, $1-\alpha$ es el **coeficiente
  de confianza**: «la fracción de veces, en muestreo repetido, que los intervalos construidos contienen al parámetro
  objetivo». **Método del pivote:** una cantidad que (1) depende de la muestra y de $\theta$, siendo $\theta$ la única
  incógnita, y (2) cuya distribución no depende de $\theta$.
- **Ejemplo 8.6 (p. 411).** Con $Z=(\hat\theta-\theta)/\sigma_{\hat\theta}\sim N(0,1)$ se obtiene
  $\hat\theta\pm z_{\alpha/2}\sigma_{\hat\theta}$. Unir dos límites unilaterales de nivel $1-\alpha$ da un intervalo
  de nivel $1-2\alpha$ (p. 412).
- **Sección 8.6 (p. 411–415).** Intervalos de muestra grande para $\mu$, $p$, $\mu_1-\mu_2$ y $p_1-p_2$; la Figura 8.8
  simula 24 intervalos para $p$.
- **Sección 8.7 (p. 421–424).** Tamaño muestral: $z_{\alpha/2}\sigma_{\hat\theta}=B$.
- **Sección 8.8 (p. 425–430).** Intervalo $t$ para $\mu$; $t$ con varianza agrupada para $\mu_1-\mu_2$.
- **Sección 8.9 (p. 434–435).** Intervalo χ² para $\sigma^2$, «muy sensible» a la normalidad.
- **Sección 8.10 (p. 437).** Resumen de robustez: $t$ es estable; χ² no; la $t$ agrupada depende de $n_1\approx n_2$.

**Errata detectada.** En el Ejemplo 8.7 (p. 413), el intervalo es del 90 % (usa $z_{.05}=1.645$), pero la última frase
dice «aproximadamente 95 %».

**Lo que no está en los capítulos 7 y 8 y por eso no se implementó:** intervalos de Welch, de Wilson, de
Clopper–Pearson y bootstrap.

---

## 3. Etapa 2: diseño matemático de los procedimientos

Todos los intervalos se obtienen con el **método del pivote**. El esquema general, siguiendo el Ejemplo 8.6:

1. Encontrar un pivote $Q(Y_1,\dots,Y_n;\theta)$ con distribución conocida que no depende de $\theta$.
2. Elegir $a<b$ con $P(a\le Q\le b)=1-\alpha$. El libro usa **colas de igual área** $\alpha/2$.
3. Reescribir el evento $\{a\le Q\le b\}$ como $\{\hat\theta_L\le\theta\le\hat\theta_U\}$. Es **el mismo evento**, así
   que tiene la misma probabilidad.

| Procedimiento | Pivote | Distribución | Intervalo bilateral | Tipo |
|---|---|---|---|---|
| $\mu$, σ conocida | $\frac{\bar Y-\mu}{\sigma/\sqrt n}$ | $N(0,1)$ | $\bar Y\pm z_{\alpha/2}\sigma/\sqrt n$ | Exacto si normal (Teo. 7.1); asintótico si no (Teo. 7.4) |
| $\mu$, muestra grande | $\frac{\bar Y-\mu}{S/\sqrt n}$ | $\approx N(0,1)$ | $\bar Y\pm z_{\alpha/2}S/\sqrt n$ | Asintótico (Sec. 8.6, Ej. 8.7) |
| $\mu$, $t$ | $\frac{\bar Y-\mu}{S/\sqrt n}$ | $t_{n-1}$ | $\bar Y\pm t_{\alpha/2,n-1}S/\sqrt n$ | Exacto bajo normalidad (Sec. 8.8) |
| $\sigma^2$ | $\frac{(n-1)S^2}{\sigma^2}$ | $\chi^2_{n-1}$ | $\left[\frac{(n-1)S^2}{\chi^2_{\alpha/2}},\frac{(n-1)S^2}{\chi^2_{1-\alpha/2}}\right]$ | Exacto bajo normalidad (Sec. 8.9) |
| $p$ | $\frac{\hat p-p}{\sqrt{\hat p\hat q/n}}$ | $\approx N(0,1)$ | $\hat p\pm z_{\alpha/2}\sqrt{\hat p\hat q/n}$ | Asintótico (Sec. 8.6) |
| $\mu_1-\mu_2$, Z | $\frac{(\bar Y_1-\bar Y_2)-(\mu_1-\mu_2)}{\sqrt{S_1^2/n_1+S_2^2/n_2}}$ | $\approx N(0,1)$ | $(\bar Y_1-\bar Y_2)\pm z_{\alpha/2}\sqrt{\cdot}$ | Asintótico (Ej. 8.3) |
| $\mu_1-\mu_2$, $t$ agrupada | $\frac{(\bar Y_1-\bar Y_2)-(\mu_1-\mu_2)}{S_p\sqrt{1/n_1+1/n_2}}$ | $t_{n_1+n_2-2}$ | $(\bar Y_1-\bar Y_2)\pm t_{\alpha/2}S_p\sqrt{\cdot}$ | Exacto con normalidad y $\sigma_1=\sigma_2$ (Ej. 8.12) |
| $p_1-p_2$ | análogo | $\approx N(0,1)$ | $(\hat p_1-\hat p_2)\pm z_{\alpha/2}\sqrt{\cdot}$ | Asintótico (Ej. 8.8) |
| $\theta$ exponencial | $2\sum Y_i/\theta$ | $\chi^2_{2n}$ | $\left[\frac{2\sum Y_i}{\chi^2_{\alpha/2,2n}},\frac{2\sum Y_i}{\chi^2_{1-\alpha/2,2n}}\right]$ | Exacto (Ej. 8.4, Ejerc. 8.47) |
| $\sigma_2^2/\sigma_1^2$ | $\frac{\sigma_2^2}{\sigma_1^2}\frac{S_1^2}{S_2^2}$ | $F_{n_1-1,n_2-1}$ | $\left[\frac{S_2^2}{S_1^2}F_{1-\alpha/2},\frac{S_2^2}{S_1^2}F_{\alpha/2}\right]$ | Exacto bajo normalidad (Ejerc. 8.125) |

La ficha completa de cada procedimiento, con los nueve elementos que pide el proyecto, está en el **Anexo A** y en la
página «Fundamentos» de la aplicación.

### 3.1 Resultados esperados (lo que la simulación debería mostrar)

| Cantidad | Valor teórico | Fuente |
|---|---|---|
| Cobertura de un procedimiento exacto | $1-\alpha$ para todo $n$ | Sección 8.5 + teorema del pivote |
| Cobertura de uno asintótico | $c(n)\to1-\alpha$ | Teorema 7.4 |
| Amplitud del intervalo Z con σ conocida | $2z_{\alpha/2}\sigma/\sqrt n$ (fija) | Sección 8.6 |
| $E(\text{amplitud})$ del intervalo t bajo normalidad | $2t_{\alpha/2,n-1}\,\sigma\,c_4(n)/\sqrt n$ | [complementario] |
| $E(\text{amplitud})$ del intervalo χ² | $(n-1)\sigma^2\big(1/\chi^2_{1-\alpha/2}-1/\chi^2_{\alpha/2}\big)$ | $E(S^2)=\sigma^2$ (Ej. 8.1) |
| Pendiente de $\log(\text{amplitud})$ contra $\log n$ | $-1/2$ | Tabla 8.1 |
| Número de intervalos que fallan entre $B$ | $\text{Binomial}(B,\alpha)$ | independencia de las réplicas |
| Error estándar de $\hat c$ | $\sqrt{c(1-c)/B}$ | Tabla 8.1 |

---

## 4. Etapa 3: arquitectura

```
app.py               menú (st.navigation)
lab/                 núcleo sin interfaz → se puede probar con pytest
  poblaciones.py     media, varianza, curtosis y muestreo de cada población
  intervalos.py      fórmulas puras y vectorizadas (un solo código para 1 o 100 000 intervalos)
  procedimientos.py  ficha matemática + función de cálculo de cada procedimiento
  motor.py           Monte Carlo por lotes, reproducible
  teoria.py          resultados teóricos y complementarios
  graficos.py        figuras Plotly
  ui.py              componentes de Streamlit
paginas/             un archivo por experimento
tests/               pruebas
```

La separación entre `lab/` (matemática) y `paginas/` (interfaz) permite **probar la matemática sin abrir la
aplicación**, y garantiza que la calculadora, los experimentos y las pruebas usen exactamente las mismas fórmulas.

---

## 5. El motor de simulación

### 5.1 Algoritmo

Para un escenario (procedimiento, población, $n$, $B$, $\alpha$, tipo de intervalo, semilla):

1. Crear el generador `numpy.random.default_rng(semilla)`.
2. Para $b=1,\dots,B$ (por lotes): generar $Y_{b1},\dots,Y_{bn}$ i.i.d. de la población y guardar **solo** los
   estadísticos que necesita el intervalo: $\bar y_b$, $s_b^2$ y $\sum_i y_{bi}$.
3. Aplicar la fórmula del intervalo a los $B$ estadísticos a la vez (operación vectorizada): $(L_b,U_b)$.
4. Calcular $\mathbf 1\{L_b\le\theta\le U_b\}$, la amplitud $U_b-L_b$ y resúmenes.

### 5.2 Una muestra de 100 000 frente a 100 000 muestras

- $n=100\,000$ y $B=1$: **un** intervalo, muy angosto (amplitud $\approx 2z\sigma/\sqrt{10^5}$). Contiene o no a
  $\theta$; **no permite estimar la cobertura**. La pestaña «Una sola muestra que crece» del Experimento 2 lo muestra.
- $n$ cualquiera y $B=100\,000$: **cien mil** intervalos. Permiten estimar la cobertura con error estándar
  $\sqrt{.95\cdot.05/10^5}\approx0.0007$.

Son preguntas distintas: **precisión de una estimación** frente a **fiabilidad de un procedimiento**. El costo es
proporcional a $n\times B$, y la aplicación lo muestra antes de ejecutar.

### 5.3 Memoria y límites

- Lotes de a lo sumo $4\times10^6$ números (≈ 32 MB en doble precisión). Con $n=100\,000$, cada lote tiene 40 muestras.
- Límites: $n\le100\,000$, $B\le200\,000$, $n\times B\le3\times10^8$.
- Para proporciones se genera directamente $Y\sim\text{Binomial}(n,p)$, que **tiene exactamente la distribución** de
  $\sum X_i$ (Sección 7.5). Por eso el costo no depende de $n$.
- Mediciones reales en el equipo de desarrollo (Linux, Python 3.13): 1000 muestras de tamaño 100 000 de una
  exponencial, 1.1 s y 64 MB de pico; 200 000 muestras normales de tamaño 5, 0.04 s. En un portátil con Windows
  conviene esperar tiempos varias veces mayores.

### 5.4 Reproducibilidad

- Misma semilla y mismos controles dan exactamente los mismos números. Hay una prueba que lo verifica.
- El resultado **no depende del tamaño de lote**: los generadores de NumPy consumen el flujo aleatorio en orden.
  También hay una prueba con lotes de 15 filas.
- En dos muestras, cada población usa su propio generador hijo (`SeedSequence.spawn`), lo que garantiza independencia.
- En los barridos sobre $n$, cada $n$ usa la semilla derivada $[\text{semilla},n]$.
- Los resultados se guardan en caché: volver a pulsar «Ejecutar» con los mismos controles no recalcula.

---

## 6. Los experimentos y la interpretación de cada gráfica

### Experimento 1. Construcción de intervalos

**Pregunta.** ¿Qué significa «95 % de confianza»?

**Gráfica de intervalos apilados** (análoga a la Figura 8.8). Cada línea horizontal es el intervalo de una muestra;
el punto es la estimación $\hat\theta$; la línea vertical discontinua es el verdadero $\theta$. Azul y trazo fino:
el intervalo contiene a $\theta$. Naranja, trazo grueso y marcador ×: no lo contiene.
*Cómo leerla:* los intervalos cambian de centro (y, salvo en el Z con σ conocida, de amplitud) de una muestra a otra;
$\theta$ no se mueve. Alrededor de $\alpha B$ intervalos fallan.
*Por qué:* cada intervalo es una variable aleatoria; $P(\hat\theta_L\le\theta\le\hat\theta_U)=1-\alpha$ antes de observar
la muestra. El número de fallas es $F\sim\text{Binomial}(B,\alpha)$, con $E(F)=B\alpha$ y $\sigma_F=\sqrt{B\alpha(1-\alpha)}$.
En la Figura 8.8 ($B=24$) se esperaban 1.2 fallas y hubo 1.

**Inspección individual.** Muestra la cuenta completa con los números sustituidos y las observaciones de esa muestra.
La aplicación recalcula $\bar y$ con los datos y comprueba que coincide con el usado en el intervalo.

**Proporción acumulada.** La fracción de intervalos que cubren entre los primeros $k$, en escala logarítmica de $k$.
La banda gris es $1-\alpha\pm1.96\sqrt{\alpha(1-\alpha)/k}$.
*Cómo leerla:* oscila mucho al principio y se estabiliza dentro de la banda si el procedimiento es exacto.
Es la ley de los grandes números.

### Experimento 2. Tamaño muestral

**Amplitud media contra $n$ (log-log).** Puntos: amplitud media simulada para cada $n$. Línea discontinua: valor teórico.
*Cómo leerla:* una recta de pendiente $-1/2$. Para dividir la amplitud por 10 hay que multiplicar $n$ por 100.
*Por qué:* toda amplitud es (valor crítico) × (error estándar), y el error estándar es $\sigma/\sqrt n$ (Tabla 8.1).
Con la $t$ y $n$ pequeño la amplitud queda por encima de la recta, porque $t_{\alpha/2,n-1}>z_{\alpha/2}$.
*Resultado de referencia* (exponencial θ = 10, intervalo $t$, B = 400, semilla 2026): pendiente estimada $-0.511$;
amplitud media 21.31 con $n=5$ y 0.124 con $n=100\,000$.

**Variabilidad del estimador.** Desviación estándar de $\hat\theta$ entre réplicas, con la curva $\sigma/\sqrt n$.
*Cómo leerla:* el estimador se concentra alrededor de $\theta$. Esa concentración es la que estrecha el intervalo.

**Cobertura contra $n$.** Puntos con barras de ±1.96 errores estándar de Monte Carlo; banda gris de fluctuación esperada.
*Cómo leerla:* la amplitud baja, pero la cobertura no: el intervalo se encoge al mismo ritmo que la variabilidad.
Con la exponencial y la $t$, la cobertura con $n=5$ o 10 está por debajo de 95 % (≈ 86–87 %) y se acerca a 95 % al
crecer $n$ (TCL).

**Una sola muestra que crece.** Banda: intervalo calculado con las primeras $n$ observaciones de **una** muestra.
*Cómo leerla:* se estrecha alrededor de $\theta$, pero es una sola trayectoria: no dice nada sobre cobertura.

**¿Qué $n$ necesito? (Sección 8.7).** $n=(z_{\alpha/2}\sigma/B)^2$ para $\mu$ y $n=z_{\alpha/2}^2pq/B^2$ para $p$.
Reproduce los Ejemplos 8.9 ($n=406$; 423 con $p=.5$) y 8.10 ($n=31$).

### Experimento 3. Cobertura

**Métricas.** $\hat c$, su error estándar $\sqrt{\hat c(1-\hat c)/B}$, el intervalo del 95 % para la cobertura real
(el de la Sección 8.6 aplicado a $\hat c$) y la distancia $(\hat c-(1-\alpha))/\sqrt{\alpha(1-\alpha)/B}$.
Si la distancia supera 1.96 en valor absoluto, la diferencia **no** se explica por azar.

**Barras de comparación.** Varios procedimientos aplicados a **las mismas** $B$ muestras, con barras de error.
*Resultado de referencia* (exponencial θ = 10, $n=10$, $B=10\,000$, semilla 2026):

| Procedimiento | Cobertura | Tipo |
|---|---|---|
| Pivote $2\sum Y/\theta$ | 0.9491 | Exacto |
| Z con σ conocida | 0.9560 | Aproximado (TCL) |
| $t$ | 0.8994 | Supuesto de normalidad violado |
| Z con S | 0.8695 | Aproximado (muestra pequeña) |

*Lectura:* el único exacto da 95 % dentro del error de Monte Carlo (±0.0022). La $t$ y la Z con S subcubren porque
la población es asimétrica y $n$ es pequeño.

**Cobertura contra $n$.** Curvas de cobertura de los procedimientos elegidos. Bajo normalidad se añade la curva
**exacta** de la Z con S [complementario]: $P(|T_{n-1}|\le z_{\alpha/2})$, que vale 0.878 con $n=5$, 0.918 con
$n=10$ y 0.940 con $n=30$.

**Por qué $\hat c\ne1-\alpha$.** (1) error de Monte Carlo; (2) procedimiento asintótico; (3) supuestos violados;
(4) discreción en datos binomiales. El número de réplicas necesario para precisión $E$ es $B=1.96^2c(1-c)/E^2$
(Sección 8.7 aplicada a $\hat c$): por ejemplo, 1825 para $E=0.01$ y 182 476 para $E=0.001$.

### Experimento 4. Nivel de confianza

**Intervalos anidados.** Para las mismas muestras, los intervalos del 90, 95 y 99 % (tres colores).
*Cómo leerla:* comparten centro y están anidados. Si el del 99 % falla, fallan los tres.

**Histogramas de amplitud** y **curva «precio de la confianza»**: amplitud relativa a la del 95 % en función del nivel.
*Por qué:* con las mismas muestras solo cambia el valor crítico. $A_{99}/A_{95}=z_{.005}/z_{.025}=2.5758/1.9600=1.314$
y $A_{90}/A_{95}=1.6449/1.9600=0.839$. Para la $t$ los cocientes dependen de los grados de libertad.
Cuando $1-\alpha\to1$, el valor crítico tiende a $\infty$.
*Resultado de referencia* (normal, $n=25$, $B=2000$): coberturas 0.9035, 0.9570 y 0.9935; amplitudes medias 0.677,
0.817 y 1.107.

**Compromiso.** Con $n$ fijo, más confianza implica intervalos más anchos. Para tener 99 % con la amplitud del 95 %
hay que multiplicar $n$ por $(z_{.005}/z_{.025})^2=1.727$.

### Experimento 5. Distribuciones muestrales

| Pestaña | Gráfica | Teoría | Qué observar |
|---|---|---|---|
| Media muestral | Histograma de $\bar y$ + $N(\mu,\sigma^2/n)$ + densidad exacta gamma (exponencial y gamma) | Teo. 7.1, Teo. 7.4, Tabla 7.1 | Con la exponencial y $n=5$ la asimetría de $\bar Y$ es $2/\sqrt5=0.894$ (simulada 0.901): la normal es solo aproximada. |
| Varianza muestral | Histograma de $(n-1)s^2/\sigma^2$ + $\chi^2_{n-1}$ | Teo. 7.3 | Coincide bajo normalidad. Fuera de ella la media sigue siendo $n-1$, pero la varianza no es $2(n-1)$. |
| t de Student | Histograma de $T$ + $t_{n-1}$ + $N(0,1)$ | Def. 7.2 | $P(\lvert T\rvert>z_{.025})>.05$: por eso hace falta $t$ con $n$ pequeño. |
| Independencia | Dispersión $(\bar y,s^2)$ | Teo. 7.3 | Correlación ≈ 0 bajo normalidad; positiva y fuerte con poblaciones asimétricas a la derecha. |
| Del cap. 7 al 8 | Histograma de $T$ con la región $\lvert T\rvert\le t_{\alpha/2}$ sombreada | Método del pivote | La fracción dentro de la región coincide **réplica a réplica** con la fracción de intervalos que cubren. |
| Sesgo y MSE | Histogramas de $S^2$ y $S'^2$ | Ej. 8.1, Def. 8.4 | $E(S'^2)=\frac{n-1}{n}\sigma^2$; bajo normalidad, $\mathrm{MSE}(S'^2)<\mathrm{MSE}(S^2)$ [complementario]. |
| Binomial | Barras binomiales + curva normal | Sec. 7.5, Ej. 7.11 | Con $n=25$, $p=.4$, $y=8$: exacta .274 y .120; aproximada con corrección .2709 y .1170. |

### Experimento 6. Supuestos

**χ² sin normalidad.** Cobertura contra $n$ para varias poblaciones; líneas discontinuas: límites cuando $n\to\infty$.
*Resultado de referencia* (valores por defecto de la pestaña: 95 %, $B=3000$, semilla 2026):

| Población | κ (curtosis en exceso) | $n=10$ | $n=100$ | $n=1000$ | Límite |
|---|---|---|---|---|---|
| Normal | 0 | 0.954 | 0.950 | 0.948 | 0.950 |
| Uniforme | −1.2 | 0.993 | 0.998 | 0.998 | 0.998 |
| t con 5 gl | 6 | 0.880 | 0.781 | 0.727 | 0.673 |
| Exponencial | 6 | 0.759 | 0.687 | 0.687 | 0.673 |

Con la log-normal ($s=0.75$, κ = 23.5) el límite es 0.417; simulada sola en la pestaña da 0.673 con $n=10$ y 0.459 con $n=1000$.

*Lectura:* con colas pesadas la cobertura **empeora** al crecer $n$ y converge a un valor equivocado.
*Por qué* [complementario]: $(n-1)S^2/\sigma^2\approx N\big(n-1,(n-1)(2+\kappa)\big)$, mientras que los cuantiles χ²
suponen varianza $2(n-1)$. El límite es $2\Phi\big(z_{\alpha/2}\sqrt{2/(2+\kappa)}\big)-1$.

**t sin normalidad.** Con la exponencial (valores por defecto de la pestaña): 0.881 ($n=5$), 0.927 ($n=20$), 0.945 ($n=100$), 0.947 ($n=300$); con la normal, entre 0.948 y 0.957 para todo $n$.
*Lectura:* a diferencia de la χ², converge a 95 %. El TCL sí rescata la $t$ (robustez, Sección 8.10).

**Proporción cerca de 0 o 1.** Curva de cobertura **exacta** del intervalo de Wald,
$C(p)=\sum_yP(Y=y)\mathbf 1\{p\in IC(y)\}$ [complementario], con puntos de Monte Carlo.
*Lectura:* la curva oscila por la discreción y se hunde cerca de 0 y 1. Los puntos simulados caen sobre ella, lo que
valida el motor. Con $p=.9$: cobertura exacta 0.650 si $n=10$ (Ejercicio 8.54; $P(\hat p=1)=.9^{10}=.349$) y 0.932
si $n=100$ (Ejercicio 8.55). Con $n=35$, $p=.5$ (Figura 8.8) es 0.959.

**t agrupada con varianzas distintas.** Cobertura contra $\sigma_2/\sigma_1$ para varios diseños ($n_1,n_2$).
*Resultado de referencia* (normales, $B=3000$):

| $\sigma_2/\sigma_1$ | (10, 10) | (10, 40) | (40, 10) |
|---|---|---|---|
| 1 | 0.952 | 0.948 | 0.948 |
| 2 | 0.936 | 0.994 | 0.818 |
| 4 | 0.935 | 0.999 | 0.708 |

*Lectura:* con $n_1=n_2$ es robusto; si la muestra grande viene de la población con varianza pequeña, $S_p^2$
subestima la variabilidad y el intervalo subcubre (0.708). Es lo que afirma la Sección 8.10.

---

## 7. Resultados complementarios: derivaciones

**$E(S)$ bajo normalidad.** $S=\sigma\sqrt{W/(n-1)}$ con $W\sim\chi^2_{n-1}=\text{Gamma}\big(\tfrac{n-1}{2},2\big)$.
Como $E(W^{1/2})=\sqrt2\,\Gamma(n/2)/\Gamma((n-1)/2)$ (momentos de la gamma, Sección 4.6),
$$E(S)=\sigma\,c_4(n),\qquad c_4(n)=\sqrt{\tfrac{2}{n-1}}\frac{\Gamma(n/2)}{\Gamma((n-1)/2)}<1.$$
$S$ es sesgado aunque $S^2$ no lo sea (desigualdad de Jensen).

**Cobertura exacta del intervalo de Wald.** $\hat p$ solo toma los valores $y/n$, así que
$C(p)=\sum_{y=0}^nP(Y=y)\,\mathbf 1\{p\in[\hat p_L(y),\hat p_U(y)]\}$ es una suma finita: no requiere simular.

**Cobertura de Z con S bajo normalidad.** El evento es $|T|\le z_{\alpha/2}$ con $T\sim t_{n-1}$, así que la
cobertura es $P(|T_{n-1}|\le z_{\alpha/2})<1-\alpha$.

**Límite del intervalo χ².** $(n-1)S^2=\sum(Y_i-\bar Y)^2$ es aproximadamente una suma de $n$ variables i.i.d.
$(Y_i-\mu)^2$, con varianza $\sigma^4(\kappa+2)$. Por el TCL, $W\approx N(n-1,(n-1)(2+\kappa))$. Los cuantiles χ²
son $\approx n-1\pm z\sqrt{2(n-1)}$. La cobertura tiende a $P(|N(0,1)|\le z\sqrt{2/(2+\kappa)})$.

**t agrupada.** El error estándar usado es $S_p\sqrt{1/n_1+1/n_2}$ y el correcto,
$\sqrt{\sigma_1^2/n_1+\sigma_2^2/n_2}$. Con $R^2$ igual al cociente (correcto/usado), para muestras grandes la
cobertura es $\approx2\Phi(z_{\alpha/2}/R)-1$.

---

## 8. Validación (Etapa 5)

Detalle en `docs/04_validacion.md`. En resumen, **117 pruebas automáticas** (todas pasan):

- **Ejemplos del libro:** 8.4, 8.7, 8.8, 8.11, 8.12, 8.13, 7.2–7.11, 8.2, 8.3, 8.9, 8.10 y el primer intervalo de
  la Figura 8.8.
- **Valores críticos:** 18 valores de las Tablas 4–7 citados en el texto.
- **Coberturas exactas:** t, Z, χ², pivote exponencial, t agrupada y F bajo sus supuestos (±4 errores estándar).
- **Coberturas conocidas:** Monte Carlo frente a la cobertura exacta de Wald y de Z con S.
- **Amplitudes:** frente a las fórmulas teóricas; pendiente −1/2 hasta $n=100\,000$.
- **Reproducibilidad**, independencia del tamaño de lote, recuperación exacta de muestras individuales.
- **Muestras grandes:** $n=100\,000$; $B=100\,000$; 200 muestras de 100 000 con memoria acotada.
- **Parámetros inválidos:** 10 casos de escenario y 7 de funciones.
- **Interfaz:** cada página se ejecuta y se pulsan sus botones sin errores.

---

## Anexos

- **Anexo A** (`anexo_A_fichas.md`): ficha completa de cada procedimiento.
- **Anexo B** (`anexo_B_correspondencia.md`): tabla de correspondencia entre módulos y libro.
