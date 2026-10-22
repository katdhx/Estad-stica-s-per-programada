# Documento matemático: la normalidad y la distribución F

Referencia: Wackerly, Mendenhall y Scheaffer, *Estadística matemática con aplicaciones*, 7.ª ed. Las páginas son
las del libro impreso. Lo que **no** está en los capítulos 7 y 8 se marca como **[complementario]**.

---

## 1. La pregunta

En los capítulos 7 y 8 la distribución F aparece para comparar dos varianzas: el Ejemplo 7.7, los Ejercicios 7.27
y 7.36, y el intervalo de confianza para σ₂²/σ₁² del Ejercicio 8.125. Todos estos resultados suponen que las dos
poblaciones son **normales**. El laboratorio estudia qué pasa cuando ese supuesto falla: cuánto se equivoca la F,
qué característica de la población lo decide y si aumentar n lo arregla.

La distinción central: **un teorema garantiza un resultado bajo sus hipótesis; una simulación mide lo que pasa
cuando esas hipótesis se cumplen o no**. La simulación no demuestra nada nuevo; muestra qué tan importante es
cada hipótesis.

## 2. La cadena de resultados del libro

| Eslabón | Resultado | ¿Necesita normalidad? |
|---|---|---|
| 1 | $S^2=\frac{1}{n-1}\sum(Y_i-\bar Y)^2$ y $E(S^2)=\sigma^2$ (Ejemplo 8.1, p. 398) | No: vale con cualquier población de varianza finita |
| 2 | $W=(n-1)S^2/\sigma^2\sim\chi^2_{n-1}$ (Teorema 7.3, p. 357) | **Sí** |
| 3 | Si $W_1\sim\chi^2_{\nu_1}$ y $W_2\sim\chi^2_{\nu_2}$ son independientes, $\frac{W_1/\nu_1}{W_2/\nu_2}\sim F(\nu_1,\nu_2)$ (Definición 7.3, p. 362) | Necesita que $W_1,W_2$ sean χ² |
| 4 | $F^*=\dfrac{S_1^2/\sigma_1^2}{S_2^2/\sigma_2^2}\sim F(n_1-1,n_2-1)$ (p. 362) | Hereda la normalidad del eslabón 2 |

La independencia entre $W_1$ y $W_2$ se cumple siempre, porque las dos muestras son independientes. Lo que falla
sin normalidad es el eslabón 2, y la F lo hereda.

**Por qué el Teorema 7.3 necesita normalidad.** El libro lo demuestra para n = 2:
$(n-1)S^2/\sigma^2=\big((Y_1-Y_2)/\sqrt{2\sigma^2}\big)^2$, que es el cuadrado de una normal estándar porque
$Y_1-Y_2$ es normal (Teorema 6.3). Si las $Y_i$ no son normales, $Y_1-Y_2$ no es normal y su cuadrado no es χ²₁.
La demostración general está en el Ejercicio 13.93.

## 3. Lo que la F promete

- **Ejemplo 7.7 (p. 363).** $n_1=6$, $n_2=10$, varianzas iguales: $P(S_1^2/S_2^2\le b)=.95$ da
  $b=F_{.05}(5,9)=3.48$. La F promete que el cociente pasa de 3.48 solo el 5 % de las veces.
- **Ejercicio 7.27 (p. 367).** Mismos tamaños: $P(S_1^2/S_2^2>2)=0.1727$ y $P(S_1^2/S_2^2<0.5)=0.2304$.
- **Ejercicio 7.36 (p. 368).** Si $\sigma_1^2=2\sigma_2^2$, $S_1^2/S_2^2=2F$ y $b=2F_{.05}(9,7)=2(3.68)=7.35$.
- **Ejercicio 8.125 (p. 441).** El pivote $F^*=\frac{\sigma_2^2}{\sigma_1^2}\frac{S_1^2}{S_2^2}$ da el intervalo
  $$\frac{\sigma_2^2}{\sigma_1^2}\in\left[\frac{S_2^2}{S_1^2}F_{1-\alpha/2},\ \frac{S_2^2}{S_1^2}F_{\alpha/2}\right],$$
  con $F_{1-\alpha/2}=1/F_{\alpha/2}(\nu_2,\nu_1)$ (Ejercicio 7.29).
- **Ejercicio 8.126 (p. 441).** $s_1^2=0.273$, $s_2^2=0.094$, $n_1=n_2=10$: el intervalo del 95 % para
  $\sigma_2^2/\sigma_1^2$ es $[0.0855,\ 1.386]$, que contiene el 1.

Propiedades de la F que usa la aplicación: $E(F)=\nu_2/(\nu_2-2)$ y la varianza del Ejercicio 7.34; $1/F\sim F(\nu_2,\nu_1)$
(Ejercicio 7.29); $T^2\sim F(1,\nu)$ (Ejercicio 7.33); $\nu_1F\to\chi^2_{\nu_1}$ cuando $\nu_2\to\infty$ (Ejercicio 7.31).

## 4. Cobertura del intervalo = probabilidad central de F*

Por el método del pivote (Sección 8.5, pp. 406–407), el intervalo se obtiene despejando el parámetro en
$F_{1-\alpha/2}\le F^*\le F_{\alpha/2}$. Despejar no cambia el evento, así que
$$P(\text{el intervalo contiene }\sigma_2^2/\sigma_1^2)=P(F_{1-\alpha/2}\le F^*\le F_{\alpha/2}).$$
Bajo normalidad vale $1-\alpha$ **exactamente, para todo n**. Sin normalidad es otro número. Por eso el
histograma de F* y la cobertura del intervalo cuentan la misma historia: la masa de F* que cae en las colas
naranjas es la proporción de intervalos que fallan. La aplicación verifica esta igualdad réplica por réplica
(prueba `test_cobertura_igual_a_probabilidad_central_de_F`).

El libro hace la misma advertencia para una sola varianza: los intervalos para σ² «pueden tener coeficientes de
confianza que difieren en un modo muy marcado con respecto al nivel nominal si la población muestreada no está
distribuida normalmente» (Sección 8.9, p. 435).

## 5. Por qué falla y cuánto [complementario]

Sea $\kappa=E[(Y-\mu)^4]/\sigma^4-3$ la **curtosis en exceso**: 0 para la normal, positiva con colas pesadas y
negativa con colas livianas. Con los valores esperados del capítulo 5 se deduce que, para cualquier población con
cuarto momento finito,
$$V(S^2)=\sigma^4\left[\frac{2}{n-1}+\frac{\kappa}{n}\right].$$

- Con $\kappa=0$ se recupera $V(S^2)=2\sigma^4/(n-1)$, lo mismo que implica el Teorema 7.3 porque $V(\chi^2_{n-1})=2(n-1)$.
- Con $\kappa>0$, $S^2$ varía **más** de lo que supone la χ²; F* tiene colas más pesadas que la F, cae fuera del
  intervalo central más seguido y los intervalos cubren **menos**.
- Con $\kappa<0$ pasa lo contrario: los intervalos cubren **de más** (y son más anchos de lo necesario).

**Más datos no lo arreglan.** Los dos términos, $2/(n-1)$ y $\kappa/n$, bajan al mismo ritmo, así que el cociente
entre la varianza real y la que supone la teoría normal tiende a $(2+\kappa)/2$, no a 1. Con $\ln F^*$
aproximadamente normal para n grande, la cobertura del intervalo del $100(1-\alpha)\%$ (misma forma en las dos
poblaciones, $n_1=n_2$) tiende a
$$2\,\Phi\!\left(z_{\alpha/2}\sqrt{\frac{2}{2+\kappa}}\right)-1.$$
Para la exponencial ($\kappa=6$) y 95 %: $2\Phi(1.96\cdot0.5)-1=2\Phi(0.98)-1\approx0.673$.

Contraste con el capítulo 8: para la **media**, el Teorema Central del Límite hace que el intervalo sea
aproximadamente correcto con n grande aunque la población no sea normal. Para la **varianza** no existe ese
rescate: el error queda fijo en la forma de la población.

**Lo que importa son las colas, no la asimetría.** $V(S^2)$ depende del cuarto momento. Dos poblaciones con la
misma curtosis (por ejemplo, t con 7 gl, simétrica, y gamma con α = 3, asimétrica; ambas κ = 2) dan coberturas muy
parecidas.

## 6. Las poblaciones

Cada forma se estandariza a media 0 y varianza 1 y se escala: $Y=\mu+\sigma X$, así que $V(Y)=\sigma^2$ exactamente.

| Forma | Construcción de X | Asimetría | κ | Referencia |
|---|---|---|---|---|
| Normal | Z | 0 | 0 | Sección 4.5 |
| Uniforme | U(−√3, √3) | 0 | −1.2 | Sección 4.4 |
| t de Student, ν > 2 | $T\sqrt{(\nu-2)/\nu}$ | 0 | 6/(ν−4) si ν > 4; ∞ si ν ≤ 4 | Definición 7.2 |
| Exponencial | E − 1, con E exponencial(1) | 2 | 6 | Sección 4.6 |
| Gamma(α) | $(G-\alpha)/\sqrt\alpha$ | $2/\sqrt\alpha$ | 6/α | Sección 4.6 |
| Log-normal(s) | $(e^{sZ}-m)/\sqrt v$ | crece con s | crece muy rápido con s | Ejercicios 4.182–4.183 |

La media μ no influye: $S^2$ usa $Y_i-\bar Y$, que no cambia si se suma una constante a todos los datos.

## 7. Resultados de la simulación (semilla 2026, B = 20 000, n₁ = n₂ = n, IC del 95 %)

| Forma | κ | n = 10 | n = 30 | n = 100 | n = 1000 | Límite [complementario] |
|---|---|---|---|---|---|---|
| Normal | 0 | 0.951 | 0.951 | 0.953 | 0.952 | 0.950 |
| Uniforme | −1.2 | 0.989 | 0.996 | 0.998 | 0.998 | 0.998 |
| t (7 gl) | 2 | 0.900 | 0.872 | 0.847 | 0.837 | 0.834 |
| Gamma (α = 3) | 2 | 0.886 | 0.855 | 0.847 | 0.836 | 0.834 |
| Exponencial | 6 | 0.770 | 0.718 | 0.691 | 0.677 | 0.673 |
| Log-normal (s = 0.5) | 5.9 | 0.823 | 0.758 | 0.714 | 0.684 | 0.676 |

Error estándar Monte Carlo de cada cifra: $\sqrt{p(1-p)/B}$, entre 0.0003 y 0.003.

Lecturas:
1. La normal da 0.95 para todo n, dentro del error de simulación: el resultado es **exacto**, no asintótico.
2. Las formas con colas pesadas caen por debajo y **se alejan más** al crecer n, hasta estancarse en el límite.
3. t(7) y gamma(3), con la misma κ, terminan en el mismo valor.
4. La uniforme sobrecubre.

Ejemplo 7.7 con poblaciones no normales ($n_1=6$, $n_2=10$, B = 40 000): la F promete
$P(S_1^2/S_2^2>3.48)=0.05$; con la normal se obtiene 0.048, con la t de 5 gl 0.092 y con la exponencial 0.140.

## 8. El motor de simulación

Para $b=1,\dots,B$: se generan $Y_{11},\dots,Y_{1n_1}$ y $Y_{21},\dots,Y_{2n_2}$ independientes, se calculan
$S_1^2$ y $S_2^2$ (divisor $n-1$) y con ellas $W_1$, $W_2$, $F^*$ y los límites del intervalo. Las estimaciones
son proporciones de réplicas, con error estándar $\sqrt{\hat p(1-\hat p)/B}$. Se dice que la simulación es
«compatible» con lo prometido $p_0$ si $|\hat p-p_0|/\sqrt{p_0(1-p_0)/B}\le1.96$.

Las muestras se generan por lotes (≤ 4 millones de números) y se descartan; solo se guardan $S_1^2$ y $S_2^2$.
Cada población tiene un generador propio derivado de la semilla, de modo que el resultado es reproducible e
independiente del tamaño del lote.
