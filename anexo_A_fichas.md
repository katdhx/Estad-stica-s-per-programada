# Anexo A. Fichas de los procedimientos

Generado automáticamente desde `lab/procedimientos.py`; es el mismo texto que muestra la aplicación.


## Media μ con σ conocida (Z)

**1. Parámetro.** $\mu$: La media poblacional μ = E(Yᵢ).

**2. Estimador.**

$$
\hat\mu = \bar Y = \frac{1}{n}\sum_{i=1}^{n} Y_i,\qquad E(\bar Y)=\mu,\quad V(\bar Y)=\frac{\sigma^2}{n}
$$

**3. Distribución muestral.**

$$
\bar Y \sim N\!\left(\mu,\ \tfrac{\sigma^2}{n}\right)\ \text{exacta si } Y_i\sim N(\mu,\sigma^2)\ (\text{Teorema 7.1});\ \text{aproximada para } n \text{ grande en otro caso (Teorema 7.4)}
$$

**4. Estadístico pivotal.**

$$
Z=\frac{\bar Y-\mu}{\sigma/\sqrt n}\sim N(0,1)
$$

**5. Fórmula del intervalo.**

$$
\bar Y \pm z_{\alpha/2}\,\frac{\sigma}{\sqrt n}
$$

Límites unilaterales:

$$
\text{inferior: }\bar Y - z_{\alpha}\frac{\sigma}{\sqrt n},\qquad \text{superior: }\bar Y + z_{\alpha}\frac{\sigma}{\sqrt n}
$$

**6. Supuestos.**

- Y₁, …, Yₙ es una muestra aleatoria: variables independientes e idénticamente distribuidas.
- σ es conocida.
- Para que sea exacto, la población debe ser normal (Teorema 7.1). Si no lo es, se necesita σ² < ∞ y n grande (Teorema 7.4). El libro sugiere n > 30 (p. 372).

**7. Justificación matemática.**

**Paso 1. La distribución del estimador.** Por el Teorema 7.1 (p. 353), si la población es normal,
$\bar Y$ es una combinación lineal de normales independientes con coeficientes $a_i = 1/n$, de modo que
$$\bar Y \sim N\!\left(\mu,\ \frac{\sigma^2}{n}\right).$$

**Paso 2. Estandarizar.** Restamos la media y dividimos por la desviación estándar de $\bar Y$:
$$Z=\frac{\bar Y-\mu}{\sigma/\sqrt n}\sim N(0,1).$$
$Z$ depende de la muestra y de $\mu$ (la única incógnita), y su distribución no depende de $\mu$.
Cumple las dos condiciones de una cantidad pivote (Sección 8.5, p. 407).

**Paso 3. Enunciado de probabilidad.** Con $z_{\alpha/2}$ definido por $P(Z>z_{\alpha/2})=\alpha/2$ (Figura 8.7),
$$P\left(-z_{\alpha/2}\le \frac{\bar Y-\mu}{\sigma/\sqrt n}\le z_{\alpha/2}\right)=1-\alpha.$$

**Paso 4. Despejar $\mu$** como en el Ejemplo 8.6 (p. 411–412): multiplicar por $\sigma/\sqrt n$, restar $\bar Y$ y multiplicar por $-1$
(lo que invierte las desigualdades):
$$P\left(\bar Y - z_{\alpha/2}\tfrac{\sigma}{\sqrt n}\ \le\ \mu\ \le\ \bar Y + z_{\alpha/2}\tfrac{\sigma}{\sqrt n}\right)=1-\alpha.$$

**Si la población no es normal**, el Teorema 7.4 (TCL) dice que $P(Z\le u)\to\Phi(u)$ cuando $n\to\infty$.
Entonces la probabilidad del paso 3 tiende a $1-\alpha$: el coeficiente es **aproximado**, no exacto.

**Amplitud** (no es aleatoria): $A = 2 z_{\alpha/2}\,\sigma/\sqrt n$. Al multiplicar $n$ por 4, la amplitud se reduce a la mitad.


**8. Interpretación.** Antes de observar la muestra, el intervalo aleatorio contiene a μ con probabilidad 1 − α. Después de observarla, el intervalo numérico contiene o no contiene a μ; el 1 − α describe el procedimiento en muestreo repetido, no un intervalo particular (Sección 8.6, p. 414–415).

**9. Referencias.** Teorema 7.1 (p. 353); Teorema 7.4, TCL (p. 372); Sección 8.5, método del pivote (p. 407); Ejemplo 8.6 (p. 411); Ejemplo 7.2 (p. 354).

**Tipo de resultado.** Exacto bajo normalidad; asintótico en otro caso.


## Media μ, muestra grande con S (Z)

**1. Parámetro.** $\mu$: La media poblacional μ, con σ desconocida.

**2. Estimador.**

$$
\bar Y,\qquad \hat\sigma_{\bar Y} = \frac{S}{\sqrt n},\quad S^2=\frac{1}{n-1}\sum_{i=1}^n (Y_i-\bar Y)^2
$$

**3. Distribución muestral.**

$$
\frac{\bar Y-\mu}{S/\sqrt n}\ \dot\sim\ N(0,1)\ \text{para } n \text{ grande}
$$

**4. Estadístico pivotal.**

$$
Z=\frac{\bar Y-\mu}{S/\sqrt n}\quad(\text{aproximadamente } N(0,1))
$$

**5. Fórmula del intervalo.**

$$
\bar Y \pm z_{\alpha/2}\,\frac{S}{\sqrt n}
$$

Límites unilaterales:

$$
\bar Y - z_{\alpha}\frac{S}{\sqrt n}\quad\text{o}\quad \bar Y + z_{\alpha}\frac{S}{\sqrt n}
$$

**6. Supuestos.**

- Muestra aleatoria (i.i.d.) con σ² < ∞.
- n grande: S sustituye a σ «sin demasiada pérdida de precisión» (p. 415).
- No requiere normalidad, pero es aproximado aun cuando la población es normal.

**7. Justificación matemática.**

**Paso 1.** Por la Tabla 8.1 (p. 397), $\bar Y$ es insesgado con error estándar $\sigma_{\bar Y}=\sigma/\sqrt n$,
y para $n$ grande es aproximadamente normal (Teorema 7.4).

**Paso 2.** $\sigma$ es desconocida. El libro la sustituye por $S$ (Ejemplo 8.7, p. 412–413):
«si $\sigma^2$ no se conoce y $n$ es grande, no hay demasiada pérdida de precisión si $\sigma^2$ se sustituye por $s^2$» (p. 415).

**Paso 3.** Con el método del Ejemplo 8.6 se obtiene $\bar Y \pm z_{\alpha/2} S/\sqrt n$.

**Advertencia.** El libro deja la justificación teórica formal de esta sustitución para la Sección 9.3 (p. 415),
que está fuera de los capítulos 7 y 8. En este laboratorio la comprobamos **empíricamente**:
con $n$ pequeño el intervalo cubre menos de lo nominal. Es justo la razón por la que la Sección 8.8 usa $t$.


**8. Interpretación.** En muestreo repetido, aproximadamente 100(1 − α) % de los intervalos contienen a μ. La aproximación mejora al crecer n.

**9. Referencias.** Tabla 8.1 (p. 397); Sección 8.6 (p. 411–415); Ejemplo 8.7 (p. 412); Teorema 7.4 (p. 372).

**Tipo de resultado.** Asintótico.


## Media μ con σ desconocida (t de Student)

**1. Parámetro.** $\mu$: La media poblacional μ, con σ desconocida.

**2. Estimador.**

$$
\bar Y\ \text{ y }\ S
$$

**3. Distribución muestral.**

$$
\bar Y\sim N(\mu,\sigma^2/n),\quad \frac{(n-1)S^2}{\sigma^2}\sim\chi^2_{n-1},\quad \bar Y \perp S^2\quad(\text{Teoremas 7.1 y 7.3})
$$

**4. Estadístico pivotal.**

$$
T=\frac{\bar Y-\mu}{S/\sqrt n}=\frac{Z}{\sqrt{W/(n-1)}}\sim t_{n-1}
$$

**5. Fórmula del intervalo.**

$$
\bar Y \pm t_{\alpha/2,\,n-1}\,\frac{S}{\sqrt n}
$$

Límites unilaterales:

$$
\bar Y - t_{\alpha}\frac{S}{\sqrt n}\quad\text{o}\quad \bar Y + t_{\alpha}\frac{S}{\sqrt n}
$$

**6. Supuestos.**

- Muestra aleatoria de una población normal (supuesto para que sea exacto).
- σ desconocida. Vale para cualquier n ≥ 2.
- El libro señala que es robusto: mantiene un coeficiente cercano al nominal si la población tiene forma de campana (Secciones 8.8 y 8.10).

**7. Justificación matemática.**

**Paso 1.** Por el Teorema 7.1, $Z=\sqrt n(\bar Y-\mu)/\sigma\sim N(0,1)$.

**Paso 2.** Por el Teorema 7.3 (p. 357), $W=(n-1)S^2/\sigma^2\sim\chi^2$ con $n-1$ gl, **y $\bar Y$ y $S^2$ son independientes**.
Así, $Z$ y $W$ son independientes.

**Paso 3.** La Definición 7.2 (p. 360) dice que $Z/\sqrt{W/\nu}$ tiene distribución $t$ con $\nu$ gl. Con $\nu=n-1$:
$$T=\frac{\sqrt n(\bar Y-\mu)/\sigma}{\sqrt{\dfrac{(n-1)S^2}{\sigma^2}\Big/(n-1)}}=\frac{\bar Y-\mu}{S/\sqrt n}\sim t_{n-1}.$$
Fíjate en que $\sigma$ se cancela: $T$ es un pivote que solo depende de $\mu$.

**Paso 4.** Con $P(-t_{\alpha/2}\le T\le t_{\alpha/2})=1-\alpha$ (Figura 8.10) y despejando como en el Ejemplo 8.6,
$$\bar Y \pm t_{\alpha/2,n-1}\frac{S}{\sqrt n}.$$

**Comparación con Z.** $t_{\alpha/2,n-1}>z_{\alpha/2}$ porque la $t$ tiene colas más pesadas (Figura 7.3; $V(T)=\nu/(\nu-2)>1$).
Ese margen extra compensa la variabilidad de $S$. Cuando $n\to\infty$, $t_{\alpha/2,n-1}\to z_{\alpha/2}$.
El libro dice que los intervalos «son casi equivalentes cuando los grados de libertad exceden de 30» (p. 430).

**Amplitud** (aleatoria): $A=2t_{\alpha/2,n-1}S/\sqrt n$.


**8. Interpretación.** Bajo normalidad, exactamente 100(1 − α) % de los intervalos construidos en muestreo repetido contienen a μ, sea cual sea n.

**9. Referencias.** Teorema 7.1 (p. 353); Teorema 7.3 (p. 357); Definición 7.2 (p. 360); Sección 8.8 (p. 425–430); Ejemplo 8.11 (p. 426).

**Tipo de resultado.** Exacto bajo normalidad.


## Varianza σ² (chi-cuadrado)

**1. Parámetro.** $\sigma^2$: La varianza poblacional σ² = V(Yᵢ).

**2. Estimador.**

$$
S^2=\frac{1}{n-1}\sum_{i=1}^n(Y_i-\bar Y)^2,\qquad E(S^2)=\sigma^2\ (\text{Ejemplo 8.1})
$$

**3. Distribución muestral.**

$$
\frac{(n-1)S^2}{\sigma^2}\sim\chi^2_{n-1}\quad(\text{Teorema 7.3, bajo normalidad})
$$

**4. Estadístico pivotal.**

$$
W=\frac{(n-1)S^2}{\sigma^2}\sim\chi^2_{n-1}
$$

**5. Fórmula del intervalo.**

$$
\left[\frac{(n-1)S^2}{\chi^2_{\alpha/2}},\ \frac{(n-1)S^2}{\chi^2_{1-\alpha/2}}\right]
$$

Límites unilaterales:

$$
\text{inferior: }\frac{(n-1)S^2}{\chi^2_{\alpha}},\qquad\text{superior: }\frac{(n-1)S^2}{\chi^2_{1-\alpha}}\quad(\text{Ejercicio 8.97})
$$

**6. Supuestos.**

- Muestra aleatoria de una población NORMAL. Este supuesto es crítico.
- El libro advierte que, si la población no es normal, el coeficiente real «puede diferir en forma marcada» del nominal (Secciones 8.9 y 8.10).

**7. Justificación matemática.**

**Paso 1.** Por el Teorema 7.3, $W=(n-1)S^2/\sigma^2\sim\chi^2_{n-1}$. Depende solo de la muestra y de $\sigma^2$,
y su distribución no depende de $\sigma^2$: es un pivote.

**Paso 2.** La $\chi^2$ no es simétrica. El libro elige **colas de igual área** (Figura 8.11, p. 435), sin buscar el intervalo más corto:
$$P\left(\chi^2_{1-\alpha/2}\le \frac{(n-1)S^2}{\sigma^2}\le\chi^2_{\alpha/2}\right)=1-\alpha.$$
Recuerda que el subíndice es el área de la cola **superior**, así que $\chi^2_{1-\alpha/2}$ es el cuantil pequeño.

**Paso 3. Invertir.** Todos los términos son positivos, de modo que al tomar recíprocos se invierte el orden.
Al multiplicar por $(n-1)S^2$:
$$\frac{(n-1)S^2}{\chi^2_{\alpha/2}}\le \sigma^2\le \frac{(n-1)S^2}{\chi^2_{1-\alpha/2}}.$$

**Por qué es frágil.** El Teorema 7.3 usa la normalidad de forma esencial, y aquí no hay ningún TCL que lo rescate a medida que crece $n$.
El Experimento 6 lo muestra con números.

**Para σ:** basta sacar la raíz cuadrada de ambos límites (Ejercicio 8.98).


**8. Interpretación.** Bajo normalidad, 100(1 − α) % de los intervalos contienen σ². El intervalo no está centrado en S²: es asimétrico porque la χ² lo es.

**9. Referencias.** Teorema 7.3 (p. 357); Ejemplo 7.5 (p. 359); Sección 8.9 (p. 434–435); Ejemplo 8.13 (p. 435); Sección 8.10 (p. 437).

**Tipo de resultado.** Exacto bajo normalidad; no se corrige con n grande.


## Media θ de una exponencial (pivote exacto)

**1. Parámetro.** $\theta$: La media θ de una población exponencial.

**2. Estimador.**

$$
\bar Y = \frac{1}{n}\sum Y_i
$$

**3. Distribución muestral.**

$$
\frac{2\sum_{i=1}^n Y_i}{\theta}\sim\chi^2_{2n}\quad(\text{Ejercicio 8.47})
$$

**4. Estadístico pivotal.**

$$
U=\frac{2\sum_{i=1}^n Y_i}{\theta}\sim\chi^2_{2n}
$$

**5. Fórmula del intervalo.**

$$
\left[\frac{2\sum Y_i}{\chi^2_{\alpha/2,\,2n}},\ \frac{2\sum Y_i}{\chi^2_{1-\alpha/2,\,2n}}\right]
$$

Límites unilaterales:

$$
\frac{2\sum Y_i}{\chi^2_{\alpha,2n}}\quad\text{o}\quad\frac{2\sum Y_i}{\chi^2_{1-\alpha,2n}}
$$

**6. Supuestos.**

- Muestra aleatoria de una población exponencial con media θ.

**7. Justificación matemática.**

Este procedimiento ilustra el **método del pivote** de la Sección 8.5 con una distribución que no es normal.

**Paso 1 (Ejemplo 8.4, p. 407).** Si $Y\sim$ Exponencial($\theta$), entonces $U=Y/\theta\sim$ Exponencial(1),
cuya distribución no depende de $\theta$.

**Paso 2 (Ejercicios 8.46 y 8.47).** Con funciones generadoras de momentos: $m_{2Y/\theta}(t)=(1-2t)^{-1}$, que es la FGM de una $\chi^2_2$.
Por independencia, $2\sum Y_i/\theta$ tiene FGM $(1-2t)^{-n}$, es decir, $\chi^2_{2n}$.

**Paso 3.** $P(\chi^2_{1-\alpha/2}\le 2\sum Y_i/\theta\le\chi^2_{\alpha/2})=1-\alpha$. Al invertir (todo es positivo) se obtiene la fórmula.

**Verificación con el libro.** Con $n=1$ y $1-\alpha=.90$: $\chi^2_{.05,2}=5.991$ y $\chi^2_{.95,2}=0.1026$,
así que el intervalo es $(2Y/5.991,\ 2Y/0.1026)=(Y/2.996,\ Y/0.0513)$, exactamente el del Ejemplo 8.4.

Es exacto para todo $n$. Permite comparar en el Experimento 3 un intervalo **exacto** con los intervalos Z y t
(aproximados) aplicados a la misma población exponencial.


**8. Interpretación.** Para toda n, exactamente 100(1 − α) % de los intervalos contienen θ.

**9. Referencias.** Sección 8.5 (p. 406–409); Ejemplo 8.4 (p. 407); Ejercicios 8.46 y 8.47 (p. 410).

**Tipo de resultado.** Exacto (población exponencial).


## Proporción p (muestra grande)

**1. Parámetro.** $p$: La probabilidad de éxito p de un experimento binomial.

**2. Estimador.**

$$
\hat p=\frac{Y}{n},\qquad E(\hat p)=p,\quad \sigma_{\hat p}=\sqrt{\frac{pq}{n}}\ (\text{Tabla 8.1})
$$

**3. Distribución muestral.**

$$
\hat p\ \dot\sim\ N\!\left(p,\frac{pq}{n}\right)\quad(\text{Sección 7.5: TCL aplicado a } X_i\in\{0,1\})
$$

**4. Estadístico pivotal.**

$$
Z=\frac{\hat p-p}{\sqrt{\hat p\hat q/n}}\quad(\text{aproximadamente } N(0,1))
$$

**5. Fórmula del intervalo.**

$$
\hat p \pm z_{\alpha/2}\sqrt{\frac{\hat p(1-\hat p)}{n}}
$$

Límites unilaterales:

$$
\hat p - z_{\alpha}\sqrt{\hat p\hat q/n}\quad\text{o}\quad \hat p + z_{\alpha}\sqrt{\hat p\hat q/n}
$$

**6. Supuestos.**

- Y ~ Binomial(n, p): n ensayos independientes con la misma probabilidad p.
- n grande y p alejado de 0 y 1. Regla del libro: p ± 3√(pq/n) ∈ (0, 1), o n > 9·(mayor de p y q)/(menor de p y q) (p. 380 y 399).

**7. Justificación matemática.**

**Paso 1 (Sección 7.5, p. 378–379).** Escribimos $Y=\sum X_i$ con $X_i=1$ si hay éxito y $0$ si no.
Las $X_i$ son i.i.d. con $E(X_i)=p$ y $V(X_i)=p(1-p)$. Por el TCL, $\hat p=Y/n=\bar X$ es aproximadamente $N(p,\ pq/n)$.

**Paso 2 (Sección 8.6).** $Z=(\hat p-p)/\sigma_{\hat p}$ es aproximadamente pivote. Pero $\sigma_{\hat p}=\sqrt{pq/n}$ depende de $p$,
así que el libro lo evalúa en $\hat p$ (p. 414): «$\sqrt{\hat p(1-\hat p)/n}$ da una buena aproximación para $\sigma_{\hat p}$».

**Paso 3.** Por el Ejemplo 8.6: $\hat p\pm z_{\alpha/2}\sqrt{\hat p\hat q/n}$.

**Dónde falla.** Si $\hat p=0$ o $\hat p=1$, el error estándar estimado es 0 y el intervalo se reduce a un punto.
Con $p=.9$ y $n=10$ eso pasa con probabilidad $.9^{10}\approx .35$; el libro lo explora en los Ejercicios 8.54 y 8.55 (p. 417).


**8. Interpretación.** Uno tiene «95 % de confianza» porque el intervalo se obtuvo con un procedimiento que contiene el parámetro aproximadamente 95 % de las veces que se usa (p. 415, Figura 8.8).

**9. Referencias.** Sección 7.5 (p. 378–382); Tabla 8.1 (p. 397); Sección 8.6 (p. 414–415); Figura 8.8 (p. 414); Ejercicios 8.51–8.55 (p. 416–417); Ejemplo 8.2 (p. 401).

**Tipo de resultado.** Asintótico.


## Diferencia de medias μ₁ − μ₂ (muestras grandes, Z)

**1. Parámetro.** $\mu_1-\mu_2$: La diferencia entre las medias de dos poblaciones independientes.

**2. Estimador.**

$$
\bar Y_1-\bar Y_2,\qquad \sigma_{\bar Y_1-\bar Y_2}=\sqrt{\frac{\sigma_1^2}{n_1}+\frac{\sigma_2^2}{n_2}}\ (\text{Tabla 8.1})
$$

**3. Distribución muestral.**

$$
\bar Y_1-\bar Y_2\ \dot\sim\ N\!\left(\mu_1-\mu_2,\ \frac{\sigma_1^2}{n_1}+\frac{\sigma_2^2}{n_2}\right)
$$

**4. Estadístico pivotal.**

$$
Z=\frac{(\bar Y_1-\bar Y_2)-(\mu_1-\mu_2)}{\sqrt{S_1^2/n_1+S_2^2/n_2}}
$$

**5. Fórmula del intervalo.**

$$
(\bar Y_1-\bar Y_2)\pm z_{\alpha/2}\sqrt{\frac{S_1^2}{n_1}+\frac{S_2^2}{n_2}}
$$

Límites unilaterales:

$$
(\bar Y_1-\bar Y_2)\mp z_{\alpha}\sqrt{S_1^2/n_1+S_2^2/n_2}
$$

**6. Supuestos.**

- Dos muestras aleatorias independientes.
- n₁ y n₂ grandes: el libro sugiere nᵢ ≥ 30 para sustituir σᵢ² por Sᵢ² (Ejemplo 8.3, p. 402).
- No requiere varianzas iguales ni normalidad.

**7. Justificación matemática.**

**Paso 1.** Por independencia y el Teorema 5.12, $E(\bar Y_1-\bar Y_2)=\mu_1-\mu_2$ y
$V(\bar Y_1-\bar Y_2)=\sigma_1^2/n_1+\sigma_2^2/n_2$ (Sección 8.3, p. 397).

**Paso 2.** Para muestras grandes, el estimador es aproximadamente normal (p. 399: «teoremas similares para funciones de medias muestrales»).

**Paso 3.** Se sustituyen $\sigma_i^2$ por $S_i^2$ (Ejemplo 8.3) y se aplica el Ejemplo 8.6.


**8. Interpretación.** En muestreo repetido, aproximadamente 100(1 − α) % de los intervalos contienen μ₁ − μ₂.

**9. Referencias.** Tabla 8.1 (p. 397); Ejemplo 8.3 (p. 402); Sección 8.6 (p. 411–415).

**Tipo de resultado.** Asintótico.


## Diferencia de medias μ₁ − μ₂ (t con varianza agrupada)

**1. Parámetro.** $\mu_1-\mu_2$: La diferencia μ₁ − μ₂ entre dos poblaciones normales con varianza común.

**2. Estimador.**

$$
\bar Y_1-\bar Y_2,\qquad S_p^2=\frac{(n_1-1)S_1^2+(n_2-1)S_2^2}{n_1+n_2-2}
$$

**3. Distribución muestral.**

$$
\frac{(n_1+n_2-2)S_p^2}{\sigma^2}\sim\chi^2_{n_1+n_2-2}\quad(\text{Teoremas 7.2 y 7.3})
$$

**4. Estadístico pivotal.**

$$
T=\frac{(\bar Y_1-\bar Y_2)-(\mu_1-\mu_2)}{S_p\sqrt{\frac1{n_1}+\frac1{n_2}}}\sim t_{n_1+n_2-2}
$$

**5. Fórmula del intervalo.**

$$
(\bar Y_1-\bar Y_2)\pm t_{\alpha/2,\,n_1+n_2-2}\,S_p\sqrt{\frac1{n_1}+\frac1{n_2}}
$$

Límites unilaterales:

$$
(\bar Y_1-\bar Y_2)\mp t_{\alpha}\,S_p\sqrt{1/n_1+1/n_2}
$$

**6. Supuestos.**

- Poblaciones normales.
- Muestras independientes. El libro dice que es «la suposición más crítica» (p. 430).
- Varianzas iguales: σ₁² = σ₂² = σ². Si n₁ ≈ n₂ el intervalo es robusto a varianzas distintas; si n₁ y n₂ son muy distintos, el supuesto «se hace más importante» (p. 437).

**7. Justificación matemática.**

**Paso 1.** Con $\sigma_1^2=\sigma_2^2=\sigma^2$, $Z=\dfrac{(\bar Y_1-\bar Y_2)-(\mu_1-\mu_2)}{\sigma\sqrt{1/n_1+1/n_2}}\sim N(0,1)$.

**Paso 2.** Por el Teorema 7.3 aplicado a cada muestra, $(n_i-1)S_i^2/\sigma^2\sim\chi^2_{n_i-1}$, y las dos son independientes.
La suma de $\chi^2$ independientes es $\chi^2$ con la suma de los gl, así que
$W=(n_1+n_2-2)S_p^2/\sigma^2\sim\chi^2_{n_1+n_2-2}$ (p. 428).

**Paso 3.** $W$ es independiente de $Z$ (Teorema 7.3: medias independientes de varianzas). Por la Definición 7.2,
$T=Z/\sqrt{W/(n_1+n_2-2)}$ tiene distribución $t$; al simplificar, $\sigma$ se cancela.

**Paso 4.** Se despeja como siempre (Ejemplo 8.12, p. 428–429).


**8. Interpretación.** Bajo los tres supuestos, exactamente 100(1 − α) % de los intervalos contienen μ₁ − μ₂.

**9. Referencias.** Sección 8.8 (p. 427–430); Ejemplo 8.12 (p. 428); Sección 8.10 (p. 437).

**Tipo de resultado.** Exacto bajo normalidad y σ₁ = σ₂.


## Diferencia de proporciones p₁ − p₂

**1. Parámetro.** $p_1-p_2$: La diferencia entre dos probabilidades de éxito de experimentos binomiales independientes.

**2. Estimador.**

$$
\hat p_1-\hat p_2,\qquad \sigma=\sqrt{\frac{p_1q_1}{n_1}+\frac{p_2q_2}{n_2}}\ (\text{Tabla 8.1})
$$

**3. Distribución muestral.**

$$
\hat p_1-\hat p_2\ \dot\sim\ N\!\left(p_1-p_2,\ \frac{p_1q_1}{n_1}+\frac{p_2q_2}{n_2}\right)
$$

**4. Estadístico pivotal.**

$$
Z=\frac{(\hat p_1-\hat p_2)-(p_1-p_2)}{\sqrt{\hat p_1\hat q_1/n_1+\hat p_2\hat q_2/n_2}}
$$

**5. Fórmula del intervalo.**

$$
(\hat p_1-\hat p_2)\pm z_{\alpha/2}\sqrt{\frac{\hat p_1\hat q_1}{n_1}+\frac{\hat p_2\hat q_2}{n_2}}
$$

Límites unilaterales:

$$
(\hat p_1-\hat p_2)\mp z_{\alpha}\sqrt{\cdots}
$$

**6. Supuestos.**

- Dos muestras binomiales independientes.
- n₁ y n₂ grandes.

**7. Justificación matemática.**

Es el mismo razonamiento que para $\mu_1-\mu_2$, con el error estándar de la Tabla 8.1 evaluado en
$\hat p_1$ y $\hat p_2$ (Ejemplo 8.8, p. 413).


**8. Interpretación.** Aproximadamente 100(1 − α) % de los intervalos contienen p₁ − p₂ en muestreo repetido.

**9. Referencias.** Tabla 8.1 (p. 397); Ejemplo 8.8 (p. 413).

**Tipo de resultado.** Asintótico.


## Razón de varianzas σ₂²/σ₁² (F)

**1. Parámetro.** $\sigma_2^2/\sigma_1^2$: El cociente σ₂²/σ₁² de las varianzas de dos poblaciones normales.

**2. Estimador.**

$$
S_2^2/S_1^2
$$

**3. Distribución muestral.**

$$
\frac{S_1^2/\sigma_1^2}{S_2^2/\sigma_2^2}\sim F_{n_1-1,\,n_2-1}\quad(\text{Definición 7.3, p. 362})
$$

**4. Estadístico pivotal.**

$$
F=\frac{\sigma_2^2}{\sigma_1^2}\cdot\frac{S_1^2}{S_2^2}\sim F_{n_1-1,n_2-1}
$$

**5. Fórmula del intervalo.**

$$
\left[\frac{S_2^2}{S_1^2}F_{1-\alpha/2},\ \frac{S_2^2}{S_1^2}F_{\alpha/2}\right],\quad F\text{ con }(n_1-1,\,n_2-1)\text{ gl}
$$

Límites unilaterales:

$$
\frac{S_2^2}{S_1^2}F_{1-\alpha}\quad\text{o}\quad\frac{S_2^2}{S_1^2}F_{\alpha}
$$

**6. Supuestos.**

- Dos poblaciones normales y muestras independientes.
- Procede de un ejercicio complementario (8.125), no del texto principal; hereda la fragilidad del intervalo χ² ante la no normalidad.

**7. Justificación matemática.**

**Paso 1.** Por el Teorema 7.3, $W_i=(n_i-1)S_i^2/\sigma_i^2\sim\chi^2_{n_i-1}$, independientes.

**Paso 2.** Por la Definición 7.3, $F=\dfrac{W_1/(n_1-1)}{W_2/(n_2-1)}=\dfrac{S_1^2/\sigma_1^2}{S_2^2/\sigma_2^2}\sim F_{n_1-1,n_2-1}$
(p. 362). Este es el inciso (a) del Ejercicio 8.125.

**Paso 3.** $P(F_{1-\alpha/2}\le F\le F_{\alpha/2})=1-\alpha$. Al multiplicar por $S_2^2/S_1^2>0$ se aísla $\sigma_2^2/\sigma_1^2$ (inciso b).


**8. Interpretación.** Bajo normalidad, 100(1 − α) % de los intervalos contienen σ₂²/σ₁².

**9. Referencias.** Definición 7.3 (p. 362); Ejemplo 7.7 (p. 363); Ejercicio 8.125 (p. 441).

**Tipo de resultado.** Exacto bajo normalidad.
