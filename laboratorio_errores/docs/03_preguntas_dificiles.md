# Preguntas difíciles del profesor y respuestas

**1. ¿Por qué en el ejemplo de Jones α no es 0.05?**
Porque Y es discreta. α solo puede valer P(Y ≤ c | p = .5) para c entero: con n = 15, c = 3 da 0.018 y c = 4 da
0.059. No hay región con α = 0.05 exacto. El libro usa {y ≤ 2} para ilustrar los conceptos, no para fijar un nivel
convencional. (La app muestra todas las regiones posibles en una tabla.)

**2. Si aumento n dejando el mismo umbral c, ¿qué pasa con α y β?**
Con RR = {y ≤ 2} fija, al crecer n es todavía más raro ver 2 o menos éxitos, bajo cualquier p: α baja
(n = 20: 0.0002) pero **β sube** (n = 20: β(.3) = 0.965; n = 30: 0.998). Aumentar n solo ayuda si la región se
ajusta con n (por ejemplo para mantener α cerca de un valor fijo); entonces β baja. Eso es lo que hace la prueba Z
del Módulo 2, donde k = μ₀ ± z_α σ/√n cambia con n.

**3. ¿β es un número o una función?**
Una función. Hₐ: p < .5 es compuesta, así que β depende del valor verdadero: β(p) = P(Y ∉ RR | p). El libro la
evalúa en p = .3. La curva del Módulo 1 la muestra completa.

**4. ¿Qué pasa con β cuando p₁ se acerca a p₀?**
β(p₁) → 1 − α, y la potencia → α. Una alternativa muy cercana a la nula casi no se distingue con una muestra
finita.

**5. ¿Por qué hacer la región más estricta baja α pero sube β?**
En la prueba Z (Hₐ: μ > μ₀), α(k) = 1 − Φ((k − μ₀)/EE) es decreciente en k y β(k) = Φ((k − μ₁)/EE) es creciente.
Ambas dependen de la misma k: no hay k que baje las dos con μ₀, μ₁, σ y n fijos.

**6. ¿Y cómo se bajan las dos?**
Aumentando n: el EE = σ/√n se achica y las campanas se separan. Con α fijo, β(μ₁) = Φ(z_α − |μ₁ − μ₀|√n/σ) baja
con n. Para α y β dados, n = (z_α + z_β)²σ²/(μ₁ − μ₀)² (Sección 10.4).

**7. «No rechazar H₀», ¿es lo mismo que aceptarla?**
No. No rechazar puede ser un error tipo II, y su probabilidad depende del valor verdadero, que no se conoce.
Por eso se dice «no rechazar» en vez de «aceptar» salvo que se reporte β para alternativas concretas.

**8. ¿Por qué no usan los parámetros binomiales en el JSON de la prueba Z?**
Porque las fórmulas Z suponen Ȳ ~ N(μ, σ/√n) con σ conocida. p es una probabilidad de éxito y la varianza de una
binomial depende de p, no es un σ conocido independiente de la media. Mezclar ambos daría fórmulas sin sentido.

**9. En el Monte Carlo, ¿por qué la frecuencia no da exactamente el valor teórico?**
Porque es una estimación con m experimentos. Su error estándar es √(p(1 − p)/m); con m = 2 500 experimentos bajo
H₀ y α = .05, es ≈ 0.0044. Diferencias de hasta unos 2 errores estándar son normales. La app muestra esa distancia
en la última columna.

**10. ¿El Monte Carlo no es circular si genera los datos con la misma normal que supone la prueba?**
Verifica la implementación de la regla y que α y β son frecuencias de largo plazo; no prueba la robustez frente a
otros modelos. Además cada experimento genera la muestra completa (no la media directamente), así que se comprueba
también que Ȳ tiene la distribución que dice la teoría.

**11. En el juego de decisión, ¿cómo saben si hubo error?**
Solo porque es simulación: la app eligió el parámetro antes de generar los datos. En la práctica la verdad es
desconocida; la prueba solo controla la frecuencia de error de la regla.

**12. ¿La prueba de signos es realmente no paramétrica si usa la binomial?**
Sí: la binomial es la distribución del **estadístico** bajo H₀, no de las observaciones. Bajo H₀ cada observación
cae arriba de m₀ con probabilidad 1/2 sea cual sea su distribución (continua), así que Y ~ Bin(n, 1/2) sin suponer
normalidad. La app lo comprueba con una Cauchy, que ni siquiera tiene media.

**13. ¿Y cuál es el costo de la prueba de signos?**
Usa solo los signos y descarta las magnitudes: con datos normales tiene menos potencia que la prueba Z. Con colas
pesadas o asimetría fuerte puede ser la opción más segura.

**14. ¿Por qué las fórmulas de Excel usan BINOMDIST y NORMSINV y no BINOM.DIST?**
Son las funciones de compatibilidad: abren sin errores en cualquier versión de Excel y en LibreOffice. Dan los
mismos valores; en Excel en español aparecen como DISTR.BINOM, DISTR.NORM.ESTAND.INV, etc.

**15. ¿Qué supone la prueba Z con los datos que suben a la app?**
Muestra aleatoria, normalidad (o n grande para el TLC) y σ conocida. Si σ no se conoce y n es grande, se puede usar
s (pruebas de muestra grande, Sección 10.3); la app avisa cuando s y la σ supuesta difieren mucho.
