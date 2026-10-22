# Guion de sustentación (10–12 minutos)

Antes de empezar: abrir la app (`iniciar_windows.bat`), dejar preparado el libro de Excel
(página Excel → *Preparar el libro de Excel* → descargar) y abrirlo en Excel.

---

**Apertura (1 min) · página Inicio**

«En el capítulo 10 una prueba de hipótesis tiene cuatro elementos: H₀, Hₐ, un estadístico y una región de rechazo.
Con esa regla solo hay dos maneras de equivocarse: rechazar H₀ cuando es cierta, el error tipo I, con probabilidad
α; o no rechazarla cuando es falsa, el error tipo II, con probabilidad β. Hoy vamos a medir cuánto cuesta cada
equivocación y qué se puede hacer con ese costo.»

**Módulo 1: Jones (2.5 min)**

«El ejemplo del libro: entrevistamos a 15 votantes; Y es cuántos apoyan a Jones. H₀: p = 0.5 contra Hₐ: p < 0.5,
y rechazamos si Y ≤ 2. Las barras rojas son los valores con los que rechazamos aunque H₀ sea cierta: suman
α = 0.0037. Las azules, los valores con los que no rechazamos aunque el verdadero p sea 0.3: suman β = 0.873.»

*(Pulsar «Región que compara el libro: y ≤ 5».)* «Si agrandamos la región, α sube a 0.151 y β baja a 0.278.
No hay almuerzo gratis.»

*(Bajar a la curva β(p).)* «p = 0.3 es un solo punto. La alternativa es compuesta: para cada p hay un β distinto.
Cerca de 0.5 la prueba casi no distingue; lejos, casi nunca falla.»

**Módulo 2: el dilema (2.5 min)**

«Lo mismo con una media y σ conocida. Dos campanas: Ȳ bajo H₀ y bajo μ₁. La línea es la frontera k.»
*(Elegir «Muevo la frontera k a mano» y moverla.)* «Si la alejo de μ₀, la zona roja, α, se achica, pero la azul,
β, crece. Las dos dependen de la misma k y se mueven en sentido contrario.»

*(Bajar al tamaño de muestra.)* «La única salida es más datos. Con la fórmula de la sección 10.4,
n = (z_α + z_β)²σ²/(μ₁ − μ₀)², para α = 0.05 y β = 0.10 necesitamos 54 observaciones en vez de 25.»
*(Descargar JSON.)* «Esta configuración pasa a la segunda aplicación.»

**Módulo 3: Monte Carlo (1.5 min)**

«Las fórmulas dicen con qué probabilidad se equivoca la regla. Aquí repetimos el experimento 5 000 veces con
muestras completas y contamos.» *(Simular.)* «La frecuencia de error tipo I queda dentro del error Monte Carlo de
0.05; la de tipo II, cerca de 0.36. Las curvas se estabilizan dentro de la banda, que se angosta como 1/√m.»

**Excel (1.5 min)**

«Para que no tengan que creerle a Python: este libro no tiene números pegados, solo fórmulas de Excel.»
*(En Excel, hoja Binomial: cambiar c de 2 a 5.)* «α = 0.151 y β = 0.278, igual que el libro y que la app.»
*(Hoja Monte_Carlo.)* «Estas son las medias que simuló la app; Excel vuelve a aplicar la regla y cuenta los errores
con CONTAR.SI.CONJUNTO. Da lo mismo.»
*(Opcional: cambiar n en Prueba_Z, guardar, subir en la pestaña 3 y mostrar que la app se actualiza.)*

**Módulo 4: toma una decisión (1.5 min)**

«Ahora ustedes. La app decidió en secreto si H₀ es cierta.» *(Nuevo experimento; el profesor o el público decide.)*
«… y aquí está la verdad. Ojo: la conocemos solo porque es una simulación. Con datos reales nunca sabremos si
esta decisión fue un error; solo sabemos con qué frecuencia se equivoca la regla.»

**Cierre (1 min)**

«Una buena prueba no evita los errores: controla α al fijar la región de rechazo y, para controlar β, hay que
elegir bien el tamaño de muestra. Eso último es justo lo que desarrolla la segunda aplicación.»

*(Si sobra tiempo: la extensión de la prueba de signos, 1 min.)*
