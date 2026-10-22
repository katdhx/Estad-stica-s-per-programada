"""Catálogo de procedimientos de intervalos de confianza.

Cada procedimiento reúne en un solo objeto:

1. la ficha matemática que pide el proyecto (parámetro, estimador, distribución
   muestral, pivote, fórmula, supuestos, justificación, interpretación y
   referencia exacta al libro), y
2. el código que calcula el intervalo a partir de los estadísticos muestrales.

Nada de lo que se afirma aquí sobre el libro es de memoria: cada referencia se
verificó en el texto de los capítulos 7 y 8 (7.ª edición en español). Los
números de página son los del libro impreso.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from . import intervalos as ic
from .poblaciones import Poblacion

# Familias de procedimientos: determinan qué estadísticos necesita el motor.
UNA_MUESTRA = "una_muestra"          # media, varianza muestral y suma de una muestra
PROPORCION = "proporcion"            # número de éxitos de una muestra Bernoulli
DOS_MUESTRAS = "dos_muestras"        # medias y varianzas de dos muestras independientes
DOS_PROPORCIONES = "dos_proporciones"


@dataclass(frozen=True)
class Procedimiento:
    clave: str
    nombre: str
    nombre_corto: str
    familia: str
    parametro: str                 # descripción en palabras
    parametro_latex: str           # símbolo
    estimador: str                 # LaTeX
    distribucion_muestral: str     # LaTeX + texto
    pivote: str                    # LaTeX
    formula: str                   # LaTeX (bilateral)
    formula_unilateral: str        # LaTeX
    supuestos: tuple[str, ...]
    justificacion: str             # markdown con LaTeX, paso a paso
    interpretacion: str
    referencias: tuple[str, ...]
    exactitud: str                 # "exacto" | "asintótico" | descripción
    poblaciones: tuple[str, ...]   # claves de población admitidas
    calcular: Callable = field(repr=False, compare=False, hash=False, default=None)
    verdadero: Callable = field(repr=False, compare=False, hash=False, default=None)

    def es_exacto_para(self, pob1: Poblacion, pob2: Poblacion | None = None) -> bool:
        """¿El coeficiente de confianza es exactamente 1 - α para estas poblaciones?"""
        if self.clave == "media_z_sigma":
            return pob1.espec.es_normal
        if self.clave in ("media_t", "varianza_chi2"):
            return pob1.espec.es_normal
        if self.clave == "exponencial_chi2":
            return pob1.espec.es_exponencial
        if self.clave == "dif_medias_t":
            return (
                pob2 is not None
                and pob1.espec.es_normal
                and pob2.espec.es_normal
                and np.isclose(pob1.varianza(), pob2.varianza())
            )
        if self.clave == "razon_varianzas_f":
            return pob2 is not None and pob1.espec.es_normal and pob2.espec.es_normal
        return False

    def calidad(self, pob1: Poblacion, pob2: Poblacion | None = None) -> str:
        """Texto breve: exacto, aproximado o supuestos violados."""
        if self.es_exacto_para(pob1, pob2):
            return "Exacto: el coeficiente de confianza es 1 − α para todo n."
        if self.clave in ("media_t", "varianza_chi2", "dif_medias_t", "razon_varianzas_f"):
            return (
                "Supuestos violados: el resultado exacto del libro no aplica; "
                "la cobertura real puede diferir de la nominal."
            )
        if self.clave == "exponencial_chi2":
            return "Supuesto violado: el pivote 2ΣY/θ solo es χ²(2n) si la población es exponencial."
        return "Aproximado: la cobertura tiende a 1 − α cuando n → ∞ (teorema del límite central)."


# ---------------------------------------------------------------------------
# Funciones de cálculo: reciben un diccionario de estadísticos por réplica.
#   Una muestra:     media, var, suma, n
#   Proporción:      exitos, n
#   Dos muestras:    media1, var1, n1, media2, var2, n2
#   Dos proporciones exitos1, n1, exitos2, n2
# Devuelven (estimador puntual, L, U).
# ---------------------------------------------------------------------------
def _calc_media_z_sigma(e, alfa, lado, pob1, pob2=None):
    L, U = ic.media_z_sigma(e["media"], pob1.desviacion(), e["n"], alfa, lado)
    return e["media"], L, U


def _calc_media_z_s(e, alfa, lado, pob1, pob2=None):
    L, U = ic.media_z_s(e["media"], np.sqrt(e["var"]), e["n"], alfa, lado)
    return e["media"], L, U


def _calc_media_t(e, alfa, lado, pob1, pob2=None):
    L, U = ic.media_t(e["media"], np.sqrt(e["var"]), e["n"], alfa, lado)
    return e["media"], L, U


def _calc_varianza(e, alfa, lado, pob1, pob2=None):
    L, U = ic.varianza_chi2(e["var"], e["n"], alfa, lado)
    return e["var"], L, U


def _calc_exponencial(e, alfa, lado, pob1, pob2=None):
    L, U = ic.exponencial_chi2(e["suma"], e["n"], alfa, lado)
    return e["suma"] / e["n"], L, U


def _calc_wald(e, alfa, lado, pob1, pob2=None):
    ph = e["exitos"] / e["n"]
    L, U = ic.proporcion_wald(ph, e["n"], alfa, lado)
    return ph, L, U


def _calc_dif_z(e, alfa, lado, pob1, pob2=None):
    L, U = ic.dif_medias_z(e["media1"], e["media2"], e["var1"], e["var2"], e["n1"], e["n2"], alfa, lado)
    return e["media1"] - e["media2"], L, U


def _calc_dif_t(e, alfa, lado, pob1, pob2=None):
    L, U = ic.dif_medias_t(e["media1"], e["media2"], e["var1"], e["var2"], e["n1"], e["n2"], alfa, lado)
    return e["media1"] - e["media2"], L, U


def _calc_dif_p(e, alfa, lado, pob1, pob2=None):
    p1 = e["exitos1"] / e["n1"]
    p2 = e["exitos2"] / e["n2"]
    L, U = ic.dif_proporciones(p1, p2, e["n1"], e["n2"], alfa, lado)
    return p1 - p2, L, U


def _calc_razon_f(e, alfa, lado, pob1, pob2=None):
    L, U = ic.razon_varianzas_f(e["var1"], e["var2"], e["n1"], e["n2"], alfa, lado)
    return e["var2"] / e["var1"], L, U


_POB_MEDIA = ("normal", "uniforme", "exponencial", "gamma", "lognormal", "t", "dado")

# ---------------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------------
PROCEDIMIENTOS: dict[str, Procedimiento] = {}


def _registrar(p: Procedimiento) -> None:
    PROCEDIMIENTOS[p.clave] = p


_registrar(Procedimiento(
    clave="media_z_sigma",
    nombre="Media μ con σ conocida (Z)",
    nombre_corto="Z, σ conocida",
    familia=UNA_MUESTRA,
    parametro="La media poblacional μ = E(Yᵢ).",
    parametro_latex=r"\mu",
    estimador=r"\hat\mu = \bar Y = \frac{1}{n}\sum_{i=1}^{n} Y_i,\qquad E(\bar Y)=\mu,\quad V(\bar Y)=\frac{\sigma^2}{n}",
    distribucion_muestral=(
        r"\bar Y \sim N\!\left(\mu,\ \tfrac{\sigma^2}{n}\right)"
        r"\ \text{exacta si } Y_i\sim N(\mu,\sigma^2)\ (\text{Teorema 7.1});\ "
        r"\text{aproximada para } n \text{ grande en otro caso (Teorema 7.4)}"
    ),
    pivote=r"Z=\frac{\bar Y-\mu}{\sigma/\sqrt n}\sim N(0,1)",
    formula=r"\bar Y \pm z_{\alpha/2}\,\frac{\sigma}{\sqrt n}",
    formula_unilateral=r"\text{inferior: }\bar Y - z_{\alpha}\frac{\sigma}{\sqrt n},\qquad \text{superior: }\bar Y + z_{\alpha}\frac{\sigma}{\sqrt n}",
    supuestos=(
        "Y₁, …, Yₙ es una muestra aleatoria: variables independientes e idénticamente distribuidas.",
        "σ es conocida.",
        "Para que sea exacto, la población debe ser normal (Teorema 7.1). Si no lo es, "
        "se necesita σ² < ∞ y n grande (Teorema 7.4). El libro sugiere n > 30 (p. 372).",
    ),
    justificacion=r"""
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
""",
    interpretacion=(
        "Antes de observar la muestra, el intervalo aleatorio contiene a μ con probabilidad 1 − α. "
        "Después de observarla, el intervalo numérico contiene o no contiene a μ; el 1 − α describe "
        "el procedimiento en muestreo repetido, no un intervalo particular (Sección 8.6, p. 414–415)."
    ),
    referencias=(
        "Teorema 7.1 (p. 353)", "Teorema 7.4, TCL (p. 372)", "Sección 8.5, método del pivote (p. 407)",
        "Ejemplo 8.6 (p. 411)", "Ejemplo 7.2 (p. 354)",
    ),
    exactitud="Exacto bajo normalidad; asintótico en otro caso",
    poblaciones=_POB_MEDIA,
    calcular=_calc_media_z_sigma,
    verdadero=lambda p1, p2=None: p1.media(),
))

_registrar(Procedimiento(
    clave="media_z_s",
    nombre="Media μ, muestra grande con S (Z)",
    nombre_corto="Z con S",
    familia=UNA_MUESTRA,
    parametro="La media poblacional μ, con σ desconocida.",
    parametro_latex=r"\mu",
    estimador=r"\bar Y,\qquad \hat\sigma_{\bar Y} = \frac{S}{\sqrt n},\quad S^2=\frac{1}{n-1}\sum_{i=1}^n (Y_i-\bar Y)^2",
    distribucion_muestral=r"\frac{\bar Y-\mu}{S/\sqrt n}\ \dot\sim\ N(0,1)\ \text{para } n \text{ grande}",
    pivote=r"Z=\frac{\bar Y-\mu}{S/\sqrt n}\quad(\text{aproximadamente } N(0,1))",
    formula=r"\bar Y \pm z_{\alpha/2}\,\frac{S}{\sqrt n}",
    formula_unilateral=r"\bar Y - z_{\alpha}\frac{S}{\sqrt n}\quad\text{o}\quad \bar Y + z_{\alpha}\frac{S}{\sqrt n}",
    supuestos=(
        "Muestra aleatoria (i.i.d.) con σ² < ∞.",
        "n grande: S sustituye a σ «sin demasiada pérdida de precisión» (p. 415).",
        "No requiere normalidad, pero es aproximado aun cuando la población es normal.",
    ),
    justificacion=r"""
**Paso 1.** Por la Tabla 8.1 (p. 397), $\bar Y$ es insesgado con error estándar $\sigma_{\bar Y}=\sigma/\sqrt n$,
y para $n$ grande es aproximadamente normal (Teorema 7.4).

**Paso 2.** $\sigma$ es desconocida. El libro la sustituye por $S$ (Ejemplo 8.7, p. 412–413):
«si $\sigma^2$ no se conoce y $n$ es grande, no hay demasiada pérdida de precisión si $\sigma^2$ se sustituye por $s^2$» (p. 415).

**Paso 3.** Con el método del Ejemplo 8.6 se obtiene $\bar Y \pm z_{\alpha/2} S/\sqrt n$.

**Advertencia.** El libro deja la justificación teórica formal de esta sustitución para la Sección 9.3 (p. 415),
que está fuera de los capítulos 7 y 8. En este laboratorio la comprobamos **empíricamente**:
con $n$ pequeño el intervalo cubre menos de lo nominal. Es justo la razón por la que la Sección 8.8 usa $t$.
""",
    interpretacion=(
        "En muestreo repetido, aproximadamente 100(1 − α) % de los intervalos contienen a μ. "
        "La aproximación mejora al crecer n."
    ),
    referencias=("Tabla 8.1 (p. 397)", "Sección 8.6 (p. 411–415)", "Ejemplo 8.7 (p. 412)", "Teorema 7.4 (p. 372)"),
    exactitud="Asintótico",
    poblaciones=_POB_MEDIA,
    calcular=_calc_media_z_s,
    verdadero=lambda p1, p2=None: p1.media(),
))

_registrar(Procedimiento(
    clave="media_t",
    nombre="Media μ con σ desconocida (t de Student)",
    nombre_corto="t de Student",
    familia=UNA_MUESTRA,
    parametro="La media poblacional μ, con σ desconocida.",
    parametro_latex=r"\mu",
    estimador=r"\bar Y\ \text{ y }\ S",
    distribucion_muestral=(
        r"\bar Y\sim N(\mu,\sigma^2/n),\quad \frac{(n-1)S^2}{\sigma^2}\sim\chi^2_{n-1},\quad \bar Y \perp S^2"
        r"\quad(\text{Teoremas 7.1 y 7.3})"
    ),
    pivote=r"T=\frac{\bar Y-\mu}{S/\sqrt n}=\frac{Z}{\sqrt{W/(n-1)}}\sim t_{n-1}",
    formula=r"\bar Y \pm t_{\alpha/2,\,n-1}\,\frac{S}{\sqrt n}",
    formula_unilateral=r"\bar Y - t_{\alpha}\frac{S}{\sqrt n}\quad\text{o}\quad \bar Y + t_{\alpha}\frac{S}{\sqrt n}",
    supuestos=(
        "Muestra aleatoria de una población normal (supuesto para que sea exacto).",
        "σ desconocida. Vale para cualquier n ≥ 2.",
        "El libro señala que es robusto: mantiene un coeficiente cercano al nominal si la población "
        "tiene forma de campana (Secciones 8.8 y 8.10).",
    ),
    justificacion=r"""
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
""",
    interpretacion=(
        "Bajo normalidad, exactamente 100(1 − α) % de los intervalos construidos en muestreo repetido "
        "contienen a μ, sea cual sea n."
    ),
    referencias=(
        "Teorema 7.1 (p. 353)", "Teorema 7.3 (p. 357)", "Definición 7.2 (p. 360)",
        "Sección 8.8 (p. 425–430)", "Ejemplo 8.11 (p. 426)",
    ),
    exactitud="Exacto bajo normalidad",
    poblaciones=_POB_MEDIA,
    calcular=_calc_media_t,
    verdadero=lambda p1, p2=None: p1.media(),
))

_registrar(Procedimiento(
    clave="varianza_chi2",
    nombre="Varianza σ² (chi-cuadrado)",
    nombre_corto="χ² para σ²",
    familia=UNA_MUESTRA,
    parametro="La varianza poblacional σ² = V(Yᵢ).",
    parametro_latex=r"\sigma^2",
    estimador=r"S^2=\frac{1}{n-1}\sum_{i=1}^n(Y_i-\bar Y)^2,\qquad E(S^2)=\sigma^2\ (\text{Ejemplo 8.1})",
    distribucion_muestral=r"\frac{(n-1)S^2}{\sigma^2}\sim\chi^2_{n-1}\quad(\text{Teorema 7.3, bajo normalidad})",
    pivote=r"W=\frac{(n-1)S^2}{\sigma^2}\sim\chi^2_{n-1}",
    formula=r"\left[\frac{(n-1)S^2}{\chi^2_{\alpha/2}},\ \frac{(n-1)S^2}{\chi^2_{1-\alpha/2}}\right]",
    formula_unilateral=r"\text{inferior: }\frac{(n-1)S^2}{\chi^2_{\alpha}},\qquad\text{superior: }\frac{(n-1)S^2}{\chi^2_{1-\alpha}}\quad(\text{Ejercicio 8.97})",
    supuestos=(
        "Muestra aleatoria de una población NORMAL. Este supuesto es crítico.",
        "El libro advierte que, si la población no es normal, el coeficiente real «puede diferir en forma marcada» "
        "del nominal (Secciones 8.9 y 8.10).",
    ),
    justificacion=r"""
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
""",
    interpretacion=(
        "Bajo normalidad, 100(1 − α) % de los intervalos contienen σ². El intervalo no está centrado en S²: "
        "es asimétrico porque la χ² lo es."
    ),
    referencias=(
        "Teorema 7.3 (p. 357)", "Ejemplo 7.5 (p. 359)", "Sección 8.9 (p. 434–435)",
        "Ejemplo 8.13 (p. 435)", "Sección 8.10 (p. 437)",
    ),
    exactitud="Exacto bajo normalidad; no se corrige con n grande",
    poblaciones=_POB_MEDIA,
    calcular=_calc_varianza,
    verdadero=lambda p1, p2=None: p1.varianza(),
))

_registrar(Procedimiento(
    clave="exponencial_chi2",
    nombre="Media θ de una exponencial (pivote exacto)",
    nombre_corto="Pivote 2ΣY/θ",
    familia=UNA_MUESTRA,
    parametro="La media θ de una población exponencial.",
    parametro_latex=r"\theta",
    estimador=r"\bar Y = \frac{1}{n}\sum Y_i",
    distribucion_muestral=r"\frac{2\sum_{i=1}^n Y_i}{\theta}\sim\chi^2_{2n}\quad(\text{Ejercicio 8.47})",
    pivote=r"U=\frac{2\sum_{i=1}^n Y_i}{\theta}\sim\chi^2_{2n}",
    formula=r"\left[\frac{2\sum Y_i}{\chi^2_{\alpha/2,\,2n}},\ \frac{2\sum Y_i}{\chi^2_{1-\alpha/2,\,2n}}\right]",
    formula_unilateral=r"\frac{2\sum Y_i}{\chi^2_{\alpha,2n}}\quad\text{o}\quad\frac{2\sum Y_i}{\chi^2_{1-\alpha,2n}}",
    supuestos=("Muestra aleatoria de una población exponencial con media θ.",),
    justificacion=r"""
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
""",
    interpretacion="Para toda n, exactamente 100(1 − α) % de los intervalos contienen θ.",
    referencias=("Sección 8.5 (p. 406–409)", "Ejemplo 8.4 (p. 407)", "Ejercicios 8.46 y 8.47 (p. 410)"),
    exactitud="Exacto (población exponencial)",
    poblaciones=("exponencial",),
    calcular=_calc_exponencial,
    verdadero=lambda p1, p2=None: p1.media(),
))

_registrar(Procedimiento(
    clave="proporcion_wald",
    nombre="Proporción p (muestra grande)",
    nombre_corto="Proporción p",
    familia=PROPORCION,
    parametro="La probabilidad de éxito p de un experimento binomial.",
    parametro_latex=r"p",
    estimador=r"\hat p=\frac{Y}{n},\qquad E(\hat p)=p,\quad \sigma_{\hat p}=\sqrt{\frac{pq}{n}}\ (\text{Tabla 8.1})",
    distribucion_muestral=r"\hat p\ \dot\sim\ N\!\left(p,\frac{pq}{n}\right)\quad(\text{Sección 7.5: TCL aplicado a } X_i\in\{0,1\})",
    pivote=r"Z=\frac{\hat p-p}{\sqrt{\hat p\hat q/n}}\quad(\text{aproximadamente } N(0,1))",
    formula=r"\hat p \pm z_{\alpha/2}\sqrt{\frac{\hat p(1-\hat p)}{n}}",
    formula_unilateral=r"\hat p - z_{\alpha}\sqrt{\hat p\hat q/n}\quad\text{o}\quad \hat p + z_{\alpha}\sqrt{\hat p\hat q/n}",
    supuestos=(
        "Y ~ Binomial(n, p): n ensayos independientes con la misma probabilidad p.",
        "n grande y p alejado de 0 y 1. Regla del libro: p ± 3√(pq/n) ∈ (0, 1), "
        "o n > 9·(mayor de p y q)/(menor de p y q) (p. 380 y 399).",
    ),
    justificacion=r"""
**Paso 1 (Sección 7.5, p. 378–379).** Escribimos $Y=\sum X_i$ con $X_i=1$ si hay éxito y $0$ si no.
Las $X_i$ son i.i.d. con $E(X_i)=p$ y $V(X_i)=p(1-p)$. Por el TCL, $\hat p=Y/n=\bar X$ es aproximadamente $N(p,\ pq/n)$.

**Paso 2 (Sección 8.6).** $Z=(\hat p-p)/\sigma_{\hat p}$ es aproximadamente pivote. Pero $\sigma_{\hat p}=\sqrt{pq/n}$ depende de $p$,
así que el libro lo evalúa en $\hat p$ (p. 414): «$\sqrt{\hat p(1-\hat p)/n}$ da una buena aproximación para $\sigma_{\hat p}$».

**Paso 3.** Por el Ejemplo 8.6: $\hat p\pm z_{\alpha/2}\sqrt{\hat p\hat q/n}$.

**Dónde falla.** Si $\hat p=0$ o $\hat p=1$, el error estándar estimado es 0 y el intervalo se reduce a un punto.
Con $p=.9$ y $n=10$ eso pasa con probabilidad $.9^{10}\approx .35$; el libro lo explora en los Ejercicios 8.54 y 8.55 (p. 417).
""",
    interpretacion=(
        "Uno tiene «95 % de confianza» porque el intervalo se obtuvo con un procedimiento que contiene "
        "el parámetro aproximadamente 95 % de las veces que se usa (p. 415, Figura 8.8)."
    ),
    referencias=(
        "Sección 7.5 (p. 378–382)", "Tabla 8.1 (p. 397)", "Sección 8.6 (p. 414–415)", "Figura 8.8 (p. 414)",
        "Ejercicios 8.51–8.55 (p. 416–417)", "Ejemplo 8.2 (p. 401)",
    ),
    exactitud="Asintótico",
    poblaciones=("bernoulli",),
    calcular=_calc_wald,
    verdadero=lambda p1, p2=None: p1.media(),
))

_registrar(Procedimiento(
    clave="dif_medias_z",
    nombre="Diferencia de medias μ₁ − μ₂ (muestras grandes, Z)",
    nombre_corto="μ₁ − μ₂, Z",
    familia=DOS_MUESTRAS,
    parametro="La diferencia entre las medias de dos poblaciones independientes.",
    parametro_latex=r"\mu_1-\mu_2",
    estimador=r"\bar Y_1-\bar Y_2,\qquad \sigma_{\bar Y_1-\bar Y_2}=\sqrt{\frac{\sigma_1^2}{n_1}+\frac{\sigma_2^2}{n_2}}\ (\text{Tabla 8.1})",
    distribucion_muestral=r"\bar Y_1-\bar Y_2\ \dot\sim\ N\!\left(\mu_1-\mu_2,\ \frac{\sigma_1^2}{n_1}+\frac{\sigma_2^2}{n_2}\right)",
    pivote=r"Z=\frac{(\bar Y_1-\bar Y_2)-(\mu_1-\mu_2)}{\sqrt{S_1^2/n_1+S_2^2/n_2}}",
    formula=r"(\bar Y_1-\bar Y_2)\pm z_{\alpha/2}\sqrt{\frac{S_1^2}{n_1}+\frac{S_2^2}{n_2}}",
    formula_unilateral=r"(\bar Y_1-\bar Y_2)\mp z_{\alpha}\sqrt{S_1^2/n_1+S_2^2/n_2}",
    supuestos=(
        "Dos muestras aleatorias independientes.",
        "n₁ y n₂ grandes: el libro sugiere nᵢ ≥ 30 para sustituir σᵢ² por Sᵢ² (Ejemplo 8.3, p. 402).",
        "No requiere varianzas iguales ni normalidad.",
    ),
    justificacion=r"""
**Paso 1.** Por independencia y el Teorema 5.12, $E(\bar Y_1-\bar Y_2)=\mu_1-\mu_2$ y
$V(\bar Y_1-\bar Y_2)=\sigma_1^2/n_1+\sigma_2^2/n_2$ (Sección 8.3, p. 397).

**Paso 2.** Para muestras grandes, el estimador es aproximadamente normal (p. 399: «teoremas similares para funciones de medias muestrales»).

**Paso 3.** Se sustituyen $\sigma_i^2$ por $S_i^2$ (Ejemplo 8.3) y se aplica el Ejemplo 8.6.
""",
    interpretacion="En muestreo repetido, aproximadamente 100(1 − α) % de los intervalos contienen μ₁ − μ₂.",
    referencias=("Tabla 8.1 (p. 397)", "Ejemplo 8.3 (p. 402)", "Sección 8.6 (p. 411–415)"),
    exactitud="Asintótico",
    poblaciones=_POB_MEDIA,
    calcular=_calc_dif_z,
    verdadero=lambda p1, p2: p1.media() - p2.media(),
))

_registrar(Procedimiento(
    clave="dif_medias_t",
    nombre="Diferencia de medias μ₁ − μ₂ (t con varianza agrupada)",
    nombre_corto="μ₁ − μ₂, t agrupada",
    familia=DOS_MUESTRAS,
    parametro="La diferencia μ₁ − μ₂ entre dos poblaciones normales con varianza común.",
    parametro_latex=r"\mu_1-\mu_2",
    estimador=r"\bar Y_1-\bar Y_2,\qquad S_p^2=\frac{(n_1-1)S_1^2+(n_2-1)S_2^2}{n_1+n_2-2}",
    distribucion_muestral=r"\frac{(n_1+n_2-2)S_p^2}{\sigma^2}\sim\chi^2_{n_1+n_2-2}\quad(\text{Teoremas 7.2 y 7.3})",
    pivote=r"T=\frac{(\bar Y_1-\bar Y_2)-(\mu_1-\mu_2)}{S_p\sqrt{\frac1{n_1}+\frac1{n_2}}}\sim t_{n_1+n_2-2}",
    formula=r"(\bar Y_1-\bar Y_2)\pm t_{\alpha/2,\,n_1+n_2-2}\,S_p\sqrt{\frac1{n_1}+\frac1{n_2}}",
    formula_unilateral=r"(\bar Y_1-\bar Y_2)\mp t_{\alpha}\,S_p\sqrt{1/n_1+1/n_2}",
    supuestos=(
        "Poblaciones normales.",
        "Muestras independientes. El libro dice que es «la suposición más crítica» (p. 430).",
        "Varianzas iguales: σ₁² = σ₂² = σ². Si n₁ ≈ n₂ el intervalo es robusto a varianzas distintas; "
        "si n₁ y n₂ son muy distintos, el supuesto «se hace más importante» (p. 437).",
    ),
    justificacion=r"""
**Paso 1.** Con $\sigma_1^2=\sigma_2^2=\sigma^2$, $Z=\dfrac{(\bar Y_1-\bar Y_2)-(\mu_1-\mu_2)}{\sigma\sqrt{1/n_1+1/n_2}}\sim N(0,1)$.

**Paso 2.** Por el Teorema 7.3 aplicado a cada muestra, $(n_i-1)S_i^2/\sigma^2\sim\chi^2_{n_i-1}$, y las dos son independientes.
La suma de $\chi^2$ independientes es $\chi^2$ con la suma de los gl, así que
$W=(n_1+n_2-2)S_p^2/\sigma^2\sim\chi^2_{n_1+n_2-2}$ (p. 428).

**Paso 3.** $W$ es independiente de $Z$ (Teorema 7.3: medias independientes de varianzas). Por la Definición 7.2,
$T=Z/\sqrt{W/(n_1+n_2-2)}$ tiene distribución $t$; al simplificar, $\sigma$ se cancela.

**Paso 4.** Se despeja como siempre (Ejemplo 8.12, p. 428–429).
""",
    interpretacion="Bajo los tres supuestos, exactamente 100(1 − α) % de los intervalos contienen μ₁ − μ₂.",
    referencias=("Sección 8.8 (p. 427–430)", "Ejemplo 8.12 (p. 428)", "Sección 8.10 (p. 437)"),
    exactitud="Exacto bajo normalidad y σ₁ = σ₂",
    poblaciones=_POB_MEDIA,
    calcular=_calc_dif_t,
    verdadero=lambda p1, p2: p1.media() - p2.media(),
))

_registrar(Procedimiento(
    clave="dif_proporciones",
    nombre="Diferencia de proporciones p₁ − p₂",
    nombre_corto="p₁ − p₂",
    familia=DOS_PROPORCIONES,
    parametro="La diferencia entre dos probabilidades de éxito de experimentos binomiales independientes.",
    parametro_latex=r"p_1-p_2",
    estimador=r"\hat p_1-\hat p_2,\qquad \sigma=\sqrt{\frac{p_1q_1}{n_1}+\frac{p_2q_2}{n_2}}\ (\text{Tabla 8.1})",
    distribucion_muestral=r"\hat p_1-\hat p_2\ \dot\sim\ N\!\left(p_1-p_2,\ \frac{p_1q_1}{n_1}+\frac{p_2q_2}{n_2}\right)",
    pivote=r"Z=\frac{(\hat p_1-\hat p_2)-(p_1-p_2)}{\sqrt{\hat p_1\hat q_1/n_1+\hat p_2\hat q_2/n_2}}",
    formula=r"(\hat p_1-\hat p_2)\pm z_{\alpha/2}\sqrt{\frac{\hat p_1\hat q_1}{n_1}+\frac{\hat p_2\hat q_2}{n_2}}",
    formula_unilateral=r"(\hat p_1-\hat p_2)\mp z_{\alpha}\sqrt{\cdots}",
    supuestos=("Dos muestras binomiales independientes.", "n₁ y n₂ grandes."),
    justificacion=r"""
Es el mismo razonamiento que para $\mu_1-\mu_2$, con el error estándar de la Tabla 8.1 evaluado en
$\hat p_1$ y $\hat p_2$ (Ejemplo 8.8, p. 413).
""",
    interpretacion="Aproximadamente 100(1 − α) % de los intervalos contienen p₁ − p₂ en muestreo repetido.",
    referencias=("Tabla 8.1 (p. 397)", "Ejemplo 8.8 (p. 413)"),
    exactitud="Asintótico",
    poblaciones=("bernoulli",),
    calcular=_calc_dif_p,
    verdadero=lambda p1, p2: p1.media() - p2.media(),
))

_registrar(Procedimiento(
    clave="razon_varianzas_f",
    nombre="Razón de varianzas σ₂²/σ₁² (F)",
    nombre_corto="F para σ₂²/σ₁²",
    familia=DOS_MUESTRAS,
    parametro="El cociente σ₂²/σ₁² de las varianzas de dos poblaciones normales.",
    parametro_latex=r"\sigma_2^2/\sigma_1^2",
    estimador=r"S_2^2/S_1^2",
    distribucion_muestral=r"\frac{S_1^2/\sigma_1^2}{S_2^2/\sigma_2^2}\sim F_{n_1-1,\,n_2-1}\quad(\text{Definición 7.3, p. 362})",
    pivote=r"F=\frac{\sigma_2^2}{\sigma_1^2}\cdot\frac{S_1^2}{S_2^2}\sim F_{n_1-1,n_2-1}",
    formula=r"\left[\frac{S_2^2}{S_1^2}F_{1-\alpha/2},\ \frac{S_2^2}{S_1^2}F_{\alpha/2}\right],\quad F\text{ con }(n_1-1,\,n_2-1)\text{ gl}",
    formula_unilateral=r"\frac{S_2^2}{S_1^2}F_{1-\alpha}\quad\text{o}\quad\frac{S_2^2}{S_1^2}F_{\alpha}",
    supuestos=(
        "Dos poblaciones normales y muestras independientes.",
        "Procede de un ejercicio complementario (8.125), no del texto principal; hereda la fragilidad "
        "del intervalo χ² ante la no normalidad.",
    ),
    justificacion=r"""
**Paso 1.** Por el Teorema 7.3, $W_i=(n_i-1)S_i^2/\sigma_i^2\sim\chi^2_{n_i-1}$, independientes.

**Paso 2.** Por la Definición 7.3, $F=\dfrac{W_1/(n_1-1)}{W_2/(n_2-1)}=\dfrac{S_1^2/\sigma_1^2}{S_2^2/\sigma_2^2}\sim F_{n_1-1,n_2-1}$
(p. 362). Este es el inciso (a) del Ejercicio 8.125.

**Paso 3.** $P(F_{1-\alpha/2}\le F\le F_{\alpha/2})=1-\alpha$. Al multiplicar por $S_2^2/S_1^2>0$ se aísla $\sigma_2^2/\sigma_1^2$ (inciso b).
""",
    interpretacion="Bajo normalidad, 100(1 − α) % de los intervalos contienen σ₂²/σ₁².",
    referencias=("Definición 7.3 (p. 362)", "Ejemplo 7.7 (p. 363)", "Ejercicio 8.125 (p. 441)"),
    exactitud="Exacto bajo normalidad",
    poblaciones=_POB_MEDIA,
    calcular=_calc_razon_f,
    verdadero=lambda p1, p2: p2.varianza() / p1.varianza(),
))


def disponibles_para(clave_pob: str, familia: str | None = None) -> list[Procedimiento]:
    """Procedimientos aplicables a una población (y opcionalmente a una familia)."""
    return [
        p for p in PROCEDIMIENTOS.values()
        if clave_pob in p.poblaciones and (familia is None or p.familia == familia)
    ]


def por_familia(familia: str) -> list[Procedimiento]:
    return [p for p in PROCEDIMIENTOS.values() if p.familia == familia]


def requiere_varianza_finita(p: Procedimiento) -> bool:
    return p.clave in ("media_z_sigma",)
