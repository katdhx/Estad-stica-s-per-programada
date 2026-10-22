# Preguntas difíciles y respuestas

**1. ¿La simulación demuestra que la F falla sin normalidad?**
No demuestra: muestra. Una simulación mide la cobertura para escenarios concretos con un error estándar conocido
($\sqrt{\hat p(1-\hat p)/B}$, unas décimas de punto con B = 20 000). Que la exponencial dé 0.69 con n = 100 a casi
100 errores estándar de 0.95 no es azar. El argumento general es la fórmula de V(S²) y el límite
$2\Phi(z_{\alpha/2}\sqrt{2/(2+\kappa)})-1$, que la simulación confirma.

**2. ¿Por qué con la normal da 95.1 % y no 95 %?**
Porque B es finito. Con B = 20 000 el error estándar es $\sqrt{0.95\cdot0.05/20000}\approx0.0015$; 0.951 está a
menos de un error estándar. Con normalidad el resultado es exacto; la diferencia es solo ruido de simulación.

**3. ¿Por qué no mejora con n grande, si en el capítulo 8 los intervalos grandes funcionan sin normalidad?**
Esos intervalos (Sección 8.6) son para medias y proporciones, y se apoyan en el Teorema Central del Límite: la
distribución de $\bar Y$ se acerca a la normal. Aquí el estadístico es S², y el problema no es su forma sino su
**varianza**: $V(S^2)=\sigma^4[2/(n-1)+\kappa/n]$ frente a $2\sigma^4/(n-1)$ que supone la χ². El cociente tiende a
$(2+\kappa)/2\ne1$. S² sí es asintóticamente normal, pero con una varianza distinta de la que usa la F.

**4. ¿De dónde sale V(S²) = σ⁴[2/(n−1) + κ/n]? ¿Está en el libro?**
No está en los capítulos 7 y 8; por eso la marcamos como complementaria. Se obtiene desarrollando
$E[(\sum(Y_i-\bar Y)^2)^2]$ con los momentos de la población (técnicas del capítulo 5). La comprobamos de dos formas:
con κ = 0 da $2\sigma^4/(n-1)$, que coincide con $V(\chi^2_{n-1})=2(n-1)$ del Teorema 7.3, y la simulación la
reproduce para normal, exponencial, uniforme y gamma (prueba `test_varianza_de_s2`, error < 6 %).

**5. ¿Qué es la curtosis en exceso?**
$\kappa=E[(Y-\mu)^4]/\sigma^4-3$. Mide cuánta probabilidad hay en las colas comparada con la normal (que tiene
κ = 0). La uniforme tiene −1.2, la exponencial 6, la t con ν gl tiene $6/(\nu-4)$.

**6. ¿La asimetría no importa?**
Importa poco para la F. Lo que entra en V(S²) es el cuarto momento. La t(7) es simétrica y la gamma(3) es
asimétrica; ambas tienen κ = 2 y con n = 100 dan 0.847 y 0.847. Con n pequeño hay pequeñas diferencias (0.900 vs
0.886 con n = 10). Para la media (intervalos t), en cambio, la asimetría sí importa mucho.

**7. ¿Y si la población tiene κ = 0 pero no es normal?**
Entonces V(S²) coincidiría con la de la χ² y el error sería pequeño para n grande, pero la F no sería exacta: el
Teorema 7.3 exige normalidad, no solo κ = 0. Ninguna de las formas del laboratorio está en ese caso.

**8. ¿Por qué el intervalo para σ₂²/σ₁² es el mismo problema que la F?**
Por el método del pivote (Sección 8.5): el intervalo se obtiene despejando el parámetro de
$F_{1-\alpha/2}\le F^*\le F_{\alpha/2}$. Despejar no cambia el evento, así que la cobertura es exactamente
$P(F_{1-\alpha/2}\le F^*\le F_{\alpha/2})$. La aplicación lo comprueba réplica por réplica.

**9. ¿Por qué usan σ₂²/σ₁² y no σ₁²/σ₂²?**
Es la forma del Ejercicio 8.125. Para σ₁²/σ₂² se toman los recíprocos de los límites (lo hace la calculadora en el
Ejercicio 8.126).

**10. ¿Importa la media μ?**
No. S² depende de $Y_i-\bar Y$; sumar una constante a todos los datos no lo cambia. El Experimento 6 lo muestra:
con la misma semilla, μ₁ = 0 y μ₁ = 50 dan exactamente la misma cobertura.

**11. ¿Por qué estandarizan las poblaciones?**
Para que σ² sea exactamente la varianza de la población en todos los escenarios. Así lo único que cambia entre una
forma y otra es la forma misma (asimetría y colas), y la comparación es justa.

**12. ¿Por qué con colas livianas la cobertura es mayor? ¿No es bueno?**
Con κ < 0, S² varía menos de lo que supone la χ², así que el intervalo es más ancho de lo necesario. Cubre de más,
pero el «95 %» ya no significa 95 % y se pierde precisión. Ambos son errores del nivel de confianza.

**13. ¿Cómo garantizan que las dos muestras son independientes?**
Cada población usa un generador propio derivado de la semilla con `SeedSequence.spawn` de NumPy, que produce flujos
estadísticamente independientes. Además, las coberturas con normalidad coinciden con lo exacto.

**14. ¿Qué pasa con la t de 4 o menos grados de libertad?**
Su cuarto momento es infinito (κ = ∞). V(S²) no es finita y la cobertura del intervalo baja hacia 0, muy lentamente, cuando n crece.
La aplicación lo indica con κ = ∞. (Este caso solo se puede elegir en los Experimentos 1 a 4, con 2 < ν ≤ 4.)

**15. ¿Por qué la t(5.5) queda por encima de la curva en el mapa de robustez?**
La curva es un límite para n grande. La curtosis de la t con pocos grados de libertad viene de valores muy extremos
y muy raros; con n moderado casi nunca aparecen, así que la muestra se comporta como si las colas fueran menos
pesadas. Al crecer n el punto baja hacia la curva: con nuestra simulación (B = 5 000) da 0.808 con n = 100, 0.769 con n = 1000 y 0.753 con n = 5000, frente al límite 0.742.

**16. ¿Qué harían en la práctica si los datos no son normales?**
Fuera del alcance de los capítulos 7 y 8. Lo que sí se concluye de ellos es: el intervalo de la F solo es confiable
si la población es normal o muy cercana, y conviene mirar las colas de los datos (valores extremos) antes de usarlo.

**17. ¿El intervalo del Ejercicio 8.126 contiene el 1? ¿Qué significa?**
Sí: [0.0855, 1.386] para σ₂²/σ₁². Aunque s₁² es casi el triple de s₂², con 10 datos por grupo el intervalo es tan
ancho que no excluye varianzas iguales. Y además supone normalidad.

**18. ¿Cuánta memoria usa con n = 20 000?**
Las muestras se generan por lotes de a lo sumo 4 millones de números (unos 32 MB) y se descartan; solo se guardan
S₁² y S₂² de cada réplica. El límite total es B·(n₁ + n₂) ≤ 300 millones de números.
