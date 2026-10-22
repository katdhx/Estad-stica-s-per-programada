import streamlit as st

from nucleo import ui

ui.preparar()
ui.encabezado(
    "Fundamentos (capítulos 7 y 8)",
    "Todo lo que el laboratorio usa sobre la distribución F, con la notación y las páginas del libro impreso. "
    "Lo que se añade y no está en el libro se marca como complementario.",
    "Ejemplo 8.1 (p. 398), Teorema 7.3 (p. 357), Definición 7.3 (p. 362), Ejemplo 7.7 (p. 363), Ejercicios 7.27 y 7.29 "
    "(p. 367), 7.31, 7.33, 7.34 y 7.36 (p. 368), Sección 8.5 (p. 406–407), Ejercicio 8.125 (p. 441) y Sección 8.9 (p. 435).",
)

t1, t2, t3, t4 = st.tabs(["De S² a la F", "Propiedades de la F", "El intervalo para σ₂²/σ₁² (cap. 8)",
                          "Por qué importa la normalidad"])

with t1:
    st.subheader("Paso 1. La varianza muestral (Ejemplo 8.1, p. 398)")
    st.latex(r"S^2=\frac{1}{n-1}\sum_{i=1}^{n}(Y_i-\bar Y)^2,\qquad E(S^2)=\sigma^2 .")
    st.markdown("$S^2$ es insesgado para **cualquier** población con varianza finita. Este paso no necesita normalidad.")
    st.subheader("Paso 2. Teorema 7.3 (p. 357): aquí entra la normalidad")
    st.markdown(r"Si $Y_1,\dots,Y_n$ es una muestra aleatoria de una distribución **normal** con media $\mu$ y varianza $\sigma^2$:")
    st.latex(r"W=\frac{(n-1)S^2}{\sigma^2}=\frac{1}{\sigma^2}\sum_{i=1}^n (Y_i-\bar Y)^2\ \sim\ \chi^2_{n-1}.")
    st.markdown(
        r"El libro lo demuestra para $n=2$: $(n-1)S^2/\sigma^2=\big((Y_1-Y_2)/\sqrt{2\sigma^2}\big)^2=Z^2\sim\chi^2_1$. "
        r"Eso funciona porque $Y_1-Y_2$ es **normal** (Teorema 6.3). La demostración general está en el Ejercicio 13.93. "
        "**Toda la demostración se apoya en que las $Y_i$ son normales.**"
    )
    st.subheader("Paso 3. Definición 7.3 (p. 362)")
    st.markdown(r"Si $W_1\sim\chi^2_{\nu_1}$ y $W_2\sim\chi^2_{\nu_2}$ son **independientes**, entonces")
    st.latex(r"F=\frac{W_1/\nu_1}{W_2/\nu_2}\ \sim\ F(\nu_1,\nu_2).")
    st.subheader("Paso 4. Juntando los pasos (p. 362)")
    st.markdown(
        r"Con dos muestras independientes de poblaciones normales, $W_1=(n_1-1)S_1^2/\sigma_1^2$ y "
        r"$W_2=(n_2-1)S_2^2/\sigma_2^2$ son χ² independientes, con $\nu_1=n_1-1$ y $\nu_2=n_2-1$. Por la Definición 7.3:"
    )
    st.latex(r"F^*=\frac{W_1/(n_1-1)}{W_2/(n_2-1)}=\frac{S_1^2/\sigma_1^2}{S_2^2/\sigma_2^2}\ \sim\ F(n_1-1,\,n_2-1).")
    st.markdown(r"Si además $\sigma_1^2=\sigma_2^2$, los $\sigma$ se cancelan y queda $S_1^2/S_2^2\sim F(n_1-1,n_2-1)$.")
    st.subheader("Ejemplo 7.7 (p. 363): una promesa concreta de la F")
    st.markdown("Con $n_1=6$, $n_2=10$ y varianzas iguales, $P(S_1^2/S_2^2\\le b)=.95$ da $b=F_{.05}(5,9)=3.48$. "
                "Es decir, **la F promete** que el cociente de las varianzas muestrales pasa de 3.48 solo el 5 % de las veces. "
                "El laboratorio comprueba si esa promesa se cumple cuando las poblaciones no son normales.")

with t2:
    st.markdown(r"La notación del libro: $F_a$ es el valor con $P(F>F_a)=a$ (Tabla 7, Apéndice 3), es decir, el cuantil $1-a$.")
    st.markdown(
        "| Propiedad | Fórmula | Fuente |\n|---|---|---|\n"
        r"| Media | $E(F)=\dfrac{\nu_2}{\nu_2-2}$, si $\nu_2>2$ | p. 362; Ejercicio 7.34(a) |" "\n"
        r"| Varianza | $V(F)=\dfrac{2\nu_2^2(\nu_1+\nu_2-2)}{\nu_1(\nu_2-2)^2(\nu_2-4)}$, si $\nu_2>4$ | p. 362; Ejercicio 7.34(b) |" "\n"
        r"| Recíproco | $1/F\sim F(\nu_2,\nu_1)$; por eso $F_{1-a}(\nu_1,\nu_2)=1/F_a(\nu_2,\nu_1)$ | Ejercicio 7.29 (p. 367) |" "\n"
        r"| Relación con la t | $T^2\sim F(1,\nu)$ si $T\sim t_\nu$ | Ejercicio 7.33 (p. 368) |" "\n"
        r"| Relación con la χ² | Cuando $\nu_2\to\infty$, $\nu_1F\to\chi^2_{\nu_1}$ | Ejercicio 7.31 (p. 368) |"
    )
    st.markdown("La media de la F solo depende de $\\nu_2$, y es un poco mayor que 1. La densidad es asimétrica a la derecha, "
                "más cuanto menores son los grados de libertad (Figura 7.4).")

with t3:
    st.markdown("**Ejercicio 8.125 (p. 441): la F como cantidad pivote (Sección 8.5).** La cantidad")
    st.latex(r"F^*=\frac{\sigma_2^2}{\sigma_1^2}\cdot\frac{S_1^2}{S_2^2}\sim F(n_1-1,n_2-1)")
    st.markdown("depende de la muestra y del parámetro $\\sigma_2^2/\\sigma_1^2$ (lo único desconocido), y su distribución no "
                "depende de él. Cumple las dos condiciones de un pivote (p. 407). Entonces:")
    st.latex(r"P\!\left(F_{1-\alpha/2}\le F^*\le F_{\alpha/2}\right)=1-\alpha"
             r"\ \Longrightarrow\ \frac{\sigma_2^2}{\sigma_1^2}\in\left[\frac{S_2^2}{S_1^2}F_{1-\alpha/2},\ \frac{S_2^2}{S_1^2}F_{\alpha/2}\right].")
    st.markdown(
        "**La observación clave del laboratorio.** «El intervalo contiene $\\sigma_2^2/\\sigma_1^2$» y «$F^*$ cae entre "
        "$F_{1-\\alpha/2}$ y $F_{\\alpha/2}$» son **el mismo evento** escrito de dos formas. Por eso, si $F^*$ no tiene "
        "distribución F, la cobertura del intervalo deja de ser $1-\\alpha$."
    )
    st.markdown("El libro advierte lo mismo para el intervalo de una sola varianza: los intervalos para $\\sigma^2$ «pueden "
                "tener coeficientes de confianza que difieren en un modo muy marcado con respecto al nivel nominal si la "
                "población muestreada no está distribuida normalmente» (Sección 8.9, p. 435; resumen en la Sección 8.10, p. 437).")

with t4:
    st.markdown("**Resultado complementario.** No está en los capítulos 7 y 8, pero se deduce con los valores esperados del capítulo 5.")
    st.markdown(r"Para cualquier población con cuarto momento finito, si $\kappa=E[(Y-\mu)^4]/\sigma^4-3$ es la **curtosis en exceso** "
                "(qué tan pesadas son las colas comparadas con la normal):")
    st.latex(r"V(S^2)=\sigma^4\left[\frac{2}{n-1}+\frac{\kappa}{n}\right].")
    st.markdown(
        r"- Con la normal, $\kappa=0$ y $V(S^2)=2\sigma^4/(n-1)$. Es justo lo que implica el Teorema 7.3, porque "
        r"$V(\chi^2_{n-1})=2(n-1)$." "\n"
        r"- Con colas pesadas ($\kappa>0$), $S^2$ varía **más** de lo que supone la χ²; con colas livianas ($\kappa<0$), varía **menos**." "\n"
        r"- Los términos $2/(n-1)$ y $\kappa/n$ bajan al mismo ritmo cuando crece $n$, así que la proporción entre ellos **no desaparece**."
    )
    st.markdown("Por eso, con $n_1=n_2$ grandes y la misma forma en las dos poblaciones, la cobertura real del intervalo del "
                "$100(1-\\alpha)\\%$ tiende a:")
    st.latex(r"2\,\Phi\!\left(z_{\alpha/2}\sqrt{\frac{2}{2+\kappa}}\right)-1 .")
    st.markdown("Con la exponencial ($\\kappa=6$) y 95 %, eso da $2\\Phi(0.98)-1\\approx0.67$: el intervalo «del 95 %» "
                "acierta apenas dos de cada tres veces. Ojo: $\\kappa=0$ hace que la varianza de $S^2$ sea la correcta, "
                "pero **solo la normal** hace que la F sea exacta, porque eso es lo que exige el Teorema 7.3. "
                "Entre las formas del laboratorio, la normal es además la única con $\\kappa=0$.")
    st.markdown("**¿Y la asimetría?** Para la F lo que importa es sobre todo la curtosis (las colas), no la asimetría. Una t con "
                "7 gl (simétrica) y una gamma con α = 3 (asimétrica) tienen la misma curtosis, κ = 2, y fallan casi igual. "
                "El Experimento 6 lo muestra.")
