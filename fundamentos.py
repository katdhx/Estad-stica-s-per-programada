import streamlit as st

from lab import ui
from lab.procedimientos import PROCEDIMIENTOS

ui.preparar()
ui.encabezado(
    "Fundamentos matemáticos",
    "Los resultados de los capítulos 7 y 8 que sostienen cada experimento, con la notación del libro. "
    "Todo lo que se cita aquí se verificó en el texto (7.ª edición en español); las páginas son las del libro impreso.",
    "Capítulo 7 (p. 346–389) y Capítulo 8 (p. 390–443).",
)

t7, t8, tpiv, tfichas = st.tabs(
    ["Capítulo 7: distribuciones muestrales", "Capítulo 8: estimación", "Método del pivote", "Fichas de los procedimientos"]
)

with t7:
    st.subheader("Definición 7.1 (p. 347): estadístico y distribución muestral")
    st.markdown(
        "Un **estadístico** es una función de las variables aleatorias observables en una muestra y de constantes conocidas. "
        "Como es función de variables aleatorias, es una variable aleatoria y tiene distribución de probabilidad: su "
        "**distribución muestral**. El libro la describe como «un modelo teórico para el histograma de frecuencia relativa "
        "de los posibles valores del estadístico que observaríamos por medio de muestreo repetido». Ese histograma es justo "
        "lo que construye la simulación."
    )
    st.subheader("Teorema 7.1 (p. 353): la media de una muestra normal")
    st.markdown(r"Si $Y_1,\dots,Y_n$ es una muestra aleatoria de $N(\mu,\sigma^2)$, entonces")
    st.latex(r"\bar Y=\frac1n\sum_{i=1}^n Y_i \sim N\!\left(\mu_{\bar Y}=\mu,\ \sigma^2_{\bar Y}=\frac{\sigma^2}{n}\right)\qquad\Longrightarrow\qquad Z=\frac{\bar Y-\mu}{\sigma/\sqrt n}\sim N(0,1).")
    st.markdown(
        r"*Idea de la demostración:* $\bar Y=\sum a_iY_i$ con $a_i=1/n$ es una combinación lineal de normales independientes, "
        r"y el Teorema 6.3 dice que es normal. Su media es $\sum a_i\mu=\mu$ y su varianza $\sum a_i^2\sigma^2=\sigma^2/n$. "
        "**El resultado es exacto para todo n.**"
    )
    st.subheader("Teorema 7.2 (p. 356): suma de cuadrados de normales estándar")
    st.latex(r"\sum_{i=1}^n Z_i^2=\sum_{i=1}^n\left(\frac{Y_i-\mu}{\sigma}\right)^2\sim\chi^2_n .")
    st.subheader("Teorema 7.3 (p. 357): la varianza muestral")
    st.latex(r"\frac{(n-1)S^2}{\sigma^2}=\frac{1}{\sigma^2}\sum_{i=1}^n(Y_i-\bar Y)^2\sim\chi^2_{n-1},\qquad \bar Y\ \text{y}\ S^2\ \text{son independientes}.")
    st.markdown(
        r"Se pierde un grado de libertad porque $\mu$ se reemplaza por $\bar Y$. El libro demuestra el caso $n=2$: "
        r"$(n-1)S^2/\sigma^2=\big((Y_1-Y_2)/\sqrt{2\sigma^2}\big)^2=Z^2\sim\chi^2_1$. La demostración general está en el Ejercicio 13.93. "
        "**Las dos conclusiones (la χ² y la independencia) requieren normalidad**; el Experimento 5 lo muestra."
    )
    st.subheader("Definición 7.2 (p. 360): distribución t de Student")
    st.latex(r"T=\frac{Z}{\sqrt{W/\nu}}\sim t_\nu\quad\text{si } Z\sim N(0,1),\ W\sim\chi^2_\nu\ \text{independientes}.")
    st.markdown(r"Con los Teoremas 7.1 y 7.3:")
    st.latex(r"T=\frac{\sqrt n(\bar Y-\mu)/\sigma}{\sqrt{\big[(n-1)S^2/\sigma^2\big]/(n-1)}}=\sqrt n\,\frac{\bar Y-\mu}{S}\sim t_{n-1}.")
    st.markdown(r"La $t$ es simétrica, con $E(T)=0$ si $\nu>1$ y $V(T)=\nu/(\nu-2)>1$ si $\nu>2$: tiene colas más pesadas que $Z$ (Figura 7.3).")
    st.subheader("Definición 7.3 (p. 362): distribución F")
    st.latex(r"F=\frac{W_1/\nu_1}{W_2/\nu_2}\sim F_{\nu_1,\nu_2},\qquad \frac{S_1^2/\sigma_1^2}{S_2^2/\sigma_2^2}\sim F_{n_1-1,\,n_2-1}.")
    st.subheader("Teorema 7.4 (p. 372): teorema del límite central")
    st.markdown(r"Sean $Y_1,\dots,Y_n$ i.i.d. con $E(Y_i)=\mu$ y $V(Y_i)=\sigma^2<\infty$, y sea $U_n=\dfrac{\bar Y-\mu}{\sigma/\sqrt n}$. Entonces")
    st.latex(r"\lim_{n\to\infty}P(U_n\le u)=\int_{-\infty}^{u}\frac{1}{\sqrt{2\pi}}e^{-t^2/2}\,dt\quad\text{para toda }u.")
    st.markdown(
        "Es una afirmación **sobre el límite**: no dice que $U_n$ sea normal para ningún $n$ finito. El libro da la guía práctica "
        "«por lo general, un valor de n mayor que 30 asegura» una buena aproximación (p. 372). La demostración opcional "
        "(Sección 7.4, Teorema 7.5) usa funciones generadoras de momentos: $m_{U_n}(t)\\to e^{t^2/2}$."
    )
    st.subheader("Sección 7.5 (p. 378): aproximación normal a la binomial")
    st.markdown(
        r"Con $Y=\sum X_i$ y $X_i\in\{0,1\}$, el TCL implica $Y/n\ \dot\sim\ N(p,\ pq/n)$. Regla práctica: "
        r"$p\pm3\sqrt{pq/n}\in(0,1)$, o $n>9\cdot\frac{\text{mayor de }p,q}{\text{menor de }p,q}$. "
        r"Con la corrección por continuidad (Ejemplo 7.11) se aproxima $P(Y\le 8)\approx P(W\le 8.5)$."
    )

with t8:
    st.subheader("Definiciones 8.1 a 8.5 (p. 391–400)")
    st.markdown(
        r"""
- **Estimador** (Def. 8.1): una regla, a menudo una fórmula, para calcular una estimación a partir de la muestra.
- **Insesgado** (Def. 8.2): $E(\hat\theta)=\theta$. **Sesgo** (Def. 8.3): $B(\hat\theta)=E(\hat\theta)-\theta$.
- **Error cuadrático medio** (Def. 8.4): $\mathrm{MSE}(\hat\theta)=E[(\hat\theta-\theta)^2]=V(\hat\theta)+[B(\hat\theta)]^2$ (Ejercicio 8.1).
- **Error de estimación** (Def. 8.5): $\varepsilon=|\hat\theta-\theta|$. El libro usa $b=2\sigma_{\hat\theta}$ como límite: por Tchebysheff, $P(\varepsilon<2\sigma_{\hat\theta})\ge .75$, y para estimadores casi normales es cercana a .95 (Tabla 8.2).
"""
    )
    st.subheader("Ejemplo 8.1 (p. 398): S² es insesgado; S′² no")
    st.latex(r"E\left[\sum_{i=1}^n(Y_i-\bar Y)^2\right]=(n-1)\sigma^2\quad\Longrightarrow\quad E(S^2)=\sigma^2,\qquad E(S'^2)=E\!\left[\tfrac1n\textstyle\sum(Y_i-\bar Y)^2\right]=\tfrac{n-1}{n}\sigma^2.")
    st.markdown("Este resultado **no requiere normalidad**; vale para cualquier población con varianza finita.")
    st.subheader("Tabla 8.1 (p. 397): estimadores insesgados comunes")
    st.markdown(
        r"""
| Parámetro $\theta$ | Estimador $\hat\theta$ | $E(\hat\theta)$ | Error estándar $\sigma_{\hat\theta}$ |
|---|---|---|---|
| $\mu$ | $\bar Y$ | $\mu$ | $\sigma/\sqrt n$ |
| $p$ | $\hat p=Y/n$ | $p$ | $\sqrt{pq/n}$ |
| $\mu_1-\mu_2$ | $\bar Y_1-\bar Y_2$ | $\mu_1-\mu_2$ | $\sqrt{\sigma_1^2/n_1+\sigma_2^2/n_2}$ |
| $p_1-p_2$ | $\hat p_1-\hat p_2$ | $p_1-p_2$ | $\sqrt{p_1q_1/n_1+p_2q_2/n_2}$ |
"""
    )
    st.subheader("Sección 8.5 (p. 406–407): coeficiente de confianza")
    st.markdown(
        r"Si $\hat\theta_L$ y $\hat\theta_U$ son los límites (aleatorios) y $P(\hat\theta_L\le\theta\le\hat\theta_U)=1-\alpha$, "
        r"entonces $1-\alpha$ es el **coeficiente de confianza**: «la fracción de veces, en muestreo repetido, que los intervalos "
        r"construidos contienen al parámetro objetivo». También se definen los límites unilaterales: $P(\hat\theta_L\le\theta)=1-\alpha$ "
        r"y $P(\theta\le\hat\theta_U)=1-\alpha$."
    )
    st.markdown(
        r"**Combinar límites (p. 412).** Si se unen un límite inferior y uno superior, cada uno de nivel $1-\alpha$, el intervalo "
        r"bilateral resultante tiene coeficiente $1-2\alpha$. Por ejemplo, dos límites del 95 % dan un intervalo del 90 %."
    )
    st.subheader("Sección 8.7 (p. 421–424): tamaño muestral")
    st.latex(r"z_{\alpha/2}\,\sigma_{\hat\theta}=B\quad\Longrightarrow\quad n=\left(\frac{z_{\alpha/2}\,\sigma}{B}\right)^2\ \text{para }\mu,\qquad n=\frac{z_{\alpha/2}^2\,pq}{B^2}\ \text{para }p.")
    st.markdown(r"Si no se sabe nada de $p$, se usa $p=.5$, que maximiza $pq$ (Ejemplo 8.9: $n=423$).")
    st.subheader("Sección 8.10 (p. 437): resumen del libro sobre robustez")
    st.markdown(
        "- El intervalo para una media es «bastante estable» ante desviaciones moderadas de la normalidad.\n"
        "- El de μ₁ − μ₂ también lo es, y ante varianzas distintas si n₁ ≈ n₂; cuando n₁ y n₂ difieren, "
        "la suposición de varianzas iguales «se hace más importante».\n"
        "- El intervalo para σ² es «muy sensible» a la normalidad: el coeficiente real «puede diferir en forma marcada» del nominal."
    )

with tpiv:
    st.subheader("Las dos condiciones de una cantidad pivote (Sección 8.5, p. 407)")
    st.markdown(
        "1. Es una función de las mediciones muestrales y del parámetro desconocido θ, donde **θ es la única cantidad desconocida**.\n"
        "2. **Su distribución de probabilidad no depende de θ.**"
    )
    st.markdown(
        "El procedimiento lógico se basa en que la probabilidad de un evento no cambia si se multiplica por una constante "
        "positiva o se le suma una constante: si $P(a\\le Y\\le b)=.7$, entonces $P(ca\\le cY\\le cb)=.7$ y "
        "$P(a+d\\le Y+d\\le b+d)=.7$."
    )
    st.subheader("Deducción general para muestras grandes (Ejemplo 8.6, p. 411–412)")
    pasos = [
        (r"Pivote", r"Z=\frac{\hat\theta-\theta}{\sigma_{\hat\theta}}\sim N(0,1)"),
        (r"Enunciado de probabilidad (Figura 8.7)", r"P\!\left(-z_{\alpha/2}\le\frac{\hat\theta-\theta}{\sigma_{\hat\theta}}\le z_{\alpha/2}\right)=1-\alpha"),
        (r"Multiplicar por $\sigma_{\hat\theta}>0$", r"P\!\left(-z_{\alpha/2}\sigma_{\hat\theta}\le\hat\theta-\theta\le z_{\alpha/2}\sigma_{\hat\theta}\right)=1-\alpha"),
        (r"Restar $\hat\theta$", r"P\!\left(-\hat\theta-z_{\alpha/2}\sigma_{\hat\theta}\le-\theta\le-\hat\theta+z_{\alpha/2}\sigma_{\hat\theta}\right)=1-\alpha"),
        (r"Multiplicar por $-1$ (se invierten las desigualdades)", r"P\!\left(\hat\theta-z_{\alpha/2}\sigma_{\hat\theta}\le\theta\le\hat\theta+z_{\alpha/2}\sigma_{\hat\theta}\right)=1-\alpha"),
    ]
    for i, (texto, formula) in enumerate(pasos, 1):
        st.markdown(f"**Paso {i}.** {texto}:")
        st.latex(formula)
    st.markdown(
        r"Lo aleatorio son los **extremos** $\hat\theta\pm z_{\alpha/2}\sigma_{\hat\theta}$, no $\theta$. Por eso la probabilidad "
        "$1-\\alpha$ se refiere al procedimiento antes de observar la muestra."
    )
    st.subheader("Pivotes exactos con una observación (Ejemplos 8.4 y 8.5)")
    st.markdown(
        r"- **Exponencial** (Ej. 8.4): $U=Y/\theta\sim\text{Exp}(1)$. Con $P(.051\le U\le 2.996)=.90$ se obtiene $(Y/2.996,\ Y/.051)$."
        "\n"
        r"- **Uniforme en $[0,\theta]$** (Ej. 8.5): $U=Y/\theta\sim U(0,1)$, y $P(U\le .95)=.95$ da el límite inferior $Y/.95$."
    )

with tfichas:
    st.markdown(
        "Cada procedimiento implementado tiene su ficha con los nueve elementos: parámetro, estimador, distribución muestral, "
        "pivote, fórmula, supuestos, justificación, interpretación y referencia."
    )
    for proc in PROCEDIMIENTOS.values():
        ui.ficha(proc)
