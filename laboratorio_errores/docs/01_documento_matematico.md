# Documento matemático: el costo de equivocarse

Referencia: Wackerly, Mendenhall y Scheaffer, *Estadística matemática con aplicaciones*, 7.ª ed., cap. 10.

> **Antes de exponer, verifiquen en su ejemplar** los números de ejemplo y de definición que se citan abajo
> (marcados con †). Los valores numéricos están comprobados con SciPy y con las pruebas automáticas; la
> numeración se escribió de memoria del libro y no se pudo cotejar con el PDF.

## 0. Los elementos de una prueba (Sección 10.2)

Toda prueba tiene cuatro elementos:

1. **Hipótesis nula** H₀.
2. **Hipótesis alternativa** Hₐ.
3. **Estadístico de prueba**: función de la muestra con la que se decide.
4. **Región de rechazo** RR: valores del estadístico con los que se rechaza H₀.

**Definición (errores)†.** Se comete un **error tipo I** si se rechaza H₀ cuando H₀ es verdadera; su probabilidad
es α y se llama **nivel** de la prueba. Se comete un **error tipo II** si no se rechaza H₀ cuando Hₐ es verdadera;
su probabilidad es β.

**Potencia** en un valor θₐ de la alternativa: 1 − β(θₐ) = P(rechazar H₀ | θ = θₐ).

Cuadro de decisiones:

| | H₀ verdadera | Hₐ verdadera |
|---|---|---|
| Rechazar H₀ | error tipo I (α) | correcto (potencia) |
| No rechazar H₀ | correcto (1 − α) | error tipo II (β) |

---

## 1. Módulo 1: el ejemplo de Jones (Sección 10.2, ejemplos†)

**Planteamiento.** Y = número de votantes, de n = 15, que favorecen a Jones; Y ~ Binomial(15, p).
H₀: p = .5, Hₐ: p < .5. Valores pequeños de Y apoyan Hₐ, así que RR = {y ≤ 2}.

**α (exacto).**

α = P(Y ≤ 2 | p = .5) = Σ_{y=0}^{2} C(15, y)(.5)¹⁵ = (1 + 15 + 105)/32 768 = 121/32 768 = **0.00369**.

**β en el valor específico p = .3.** La alternativa es *compuesta* (todos los p < .5); el libro calcula β en un
punto:

β(.3) = P(Y > 2 | p = .3) = 1 − Σ_{y=0}^{2} C(15, y)(.3)ʸ(.7)¹⁵⁻ʸ = **0.873**, potencia = **0.127**.

**La otra región que compara el libro†:** RR = {y ≤ 5} da α = **0.151** y β(.3) = **0.278**.

**Qué muestra la app.**

- Las dos distribuciones de Y (bajo p₀ y bajo p₁) con colores: rojo = RR bajo H₀ (suma = α), azul = no rechazo bajo
  p₁ (suma = β), verde = rechazo bajo p₁ (suma = potencia).
- **Curva β(p)** = P(Y ∉ RR | p) para todo p en Hₐ. Distingue el **valor específico p₁** (un punto) de la
  **alternativa compuesta** (toda la curva). Cuando p → p₀, β(p) → 1 − α: cerca de H₀ la prueba casi no distingue.
- Tabla con todas las regiones posibles {y ≤ c}: al crecer c, α sube y β baja (intercambio con n fijo).
- Generalización: con Hₐ: p > p₀ la región es {y ≥ c}; por simetría {y ≤ c} con p equivale a {y ≥ n − c} con 1 − p.

**Por qué α no es .05.** Y es discreta: α solo toma los valores P(Y ≤ c | p₀), c = 0, 1, …. Con n = 15 y p₀ = .5,
c = 3 da α = .018 y c = 4 da α = .059; no hay región con α = .05 exacto.

---

## 2. Módulo 2: el dilema entre α y β (prueba Z, σ conocida)

**Supuestos.** Y₁, …, Yₙ m.a. de una normal con media μ y σ conocida. Entonces Ȳ ~ N(μ, σ/√n) exactamente.
EE = σ/√n.

**Regla con nivel α** (Hₐ: μ > μ₀): rechazar si Ȳ > k, con k = μ₀ + z_α·σ/√n, donde P(Z > z_α) = α.
(Con Hₐ: μ < μ₀: rechazar si Ȳ < k, k = μ₀ − z_α·σ/√n.)

**Errores en función de la frontera k** (Hₐ: μ > μ₀):

- α(k) = P(Ȳ > k | μ₀) = 1 − Φ((k − μ₀)/(σ/√n))
- β(k) = P(Ȳ ≤ k | μ₁) = Φ((k − μ₁)/(σ/√n))

**Por qué hacer la regla más estricta baja α y puede subir β.** Más estricta = k más lejos de μ₀ en la dirección
de Hₐ. Φ es creciente, así que (k − μ₀)/EE crece y α(k) **disminuye**; al mismo tiempo (k − μ₁)/EE crece y β(k)
**aumenta**. Ambas dependen de la misma k con monotonías opuestas: con μ₀, μ₁, σ y n fijos, no existe una k que
baje las dos. (En el caso inferior todo es simétrico.)

**Lo que sí rompe el dilema: n (Sección 10.4).** Con k = μ₀ + z_α·σ/√n, β(μ₁) = Φ(z_α − (μ₁ − μ₀)√n/σ), que baja
cuando n crece con α fijo. Para pedir α y β a la vez:

n = (z_α + z_β)² σ² / (μ₁ − μ₀)², redondeado hacia arriba.

Ejemplo de la app (μ₀ = 0, μ₁ = −0.4, σ = 1, n = 25, α = .05): k = −0.329, β = 0.361, potencia = 0.639.
Para β = .10 hace falta n = 54.

**Exportación JSON.** Campos mínimos: `mu0`, `mu1`, `sigma`, `n`, `alfa`, `tipo_prueba` (más `alpha`, `alternative`,
`crit` del formato anterior). Solo se exportan parámetros de la prueba Z: p de una binomial no es la media de una
normal con σ conocida, así que no se puede meter en estas fórmulas. Ejemplo: `docs/config_ejemplo_Z.json`.

---

## 3. Módulo 3: Monte Carlo

Cada experimento: (1) se elige el estado verdadero (H₀ con probabilidad π, la alternativa específica con 1 − π);
(2) se genera una muestra completa de tamaño n; (3) se calcula el estadístico (z o y); (4) se aplica la regla;
(5) se clasifica: error tipo I (H₀ verdadera y se rechaza), error tipo II (Hₐ verdadera y no se rechaza) o
decisión correcta.

- **Frecuencia empírica de error tipo I** = rechazos / experimentos con H₀ verdadera (análogo para tipo II).
- **Error Monte Carlo** = √(p̂(1 − p̂)/m): error estándar de una proporción estimada con m experimentos.
- Por la ley de los grandes números p̂ → probabilidad teórica; la banda teórica ± 1.96·EE se angosta como 1/√m.
- La columna «Diferencia / EE teórico» dice a cuántos errores estándar quedó lo simulado de lo teórico; entre
  −2 y 2 es lo esperado por azar.

Es una extensión computacional: no cambia la teoría, verifica que α y β son frecuencias de largo plazo de la regla.

---

## 4. Módulo 4: toma una decisión

La app elige en secreto H₀ o la alternativa específica (probabilidad 1/2 cada una), genera la muestra y muestra
el estadístico. Tras la decisión del público revela la regla de nivel α, su decisión, el estado verdadero y el tipo
de error. Se insiste en que la verdad se conoce **solo porque es una simulación**: con datos reales nunca se sabe si
una decisión concreta fue un error; solo se conoce la probabilidad de error de la regla.

---

## 5. Excel

El libro descargable recalcula con fórmulas de Excel lo mismo que la app:

- `Binomial`: α = BINOMDIST(c, n, p₀, TRUE); β = 1 − BINOMDIST(c, n, p₁, TRUE) (cola inferior).
- `Curva_beta`: β(p) para p = .01, …, .99.
- `Prueba_Z`: EE = σ/√n; z_α = NORMSINV(1 − α); k; α y β con NORMDIST; n = ROUNDUP((z_α + z_β)²σ²/(μ₁ − μ₀)², 0).
- `Monte_Carlo`: las medias simuladas por la app; Excel recalcula z, la decisión y el tipo de error y cuenta con
  COUNTIFS. Así se verifica la simulación con una herramienta independiente.
- `Tus_datos`: prueba Z sobre una columna de datos (ȳ = AVERAGE, z, decisión, valor p = 1 − NORMSDIST(z)).

Validado: tras recalcular con LibreOffice, todas las celdas coinciden con Python (ver `04_validacion.md`).

---

## 6. Extensión opcional: prueba de signos

X₁, …, Xₙ independientes de una población **continua** con mediana M; H₀: M = m₀.

1. Bajo H₀, por definición de mediana, P(Xᵢ > m₀) = 1/2 sin importar la forma de la población; con población
   continua P(Xᵢ = m₀) = 0.
2. Los indicadores 1{Xᵢ > m₀} son Bernoulli(1/2) independientes.
3. Y = #{Xᵢ > m₀} ~ Binomial(n, 1/2) bajo H₀.

Es la estructura del ejemplo de Jones con p₀ = .5: la RR y α se calculan con la binomial exacta, sin normalidad.
La app lo comprueba simulando poblaciones normal, exponencial desplazada, Cauchy y uniforme con la misma mediana:
las cuatro dan la misma tasa de rechazo (dentro del error Monte Carlo). Supuestos que sí se necesitan:
independencia y continuidad (con datos reales, los empates con m₀ se descartan). No se introducen Mann–Whitney ni
Wilcoxon.
