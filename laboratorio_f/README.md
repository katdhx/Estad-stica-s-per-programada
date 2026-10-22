# Laboratorio F: la normalidad y la distribución F

Segunda aplicación del proyecto de Estadística Matemática. Es independiente del laboratorio de intervalos de
confianza: no lo modifica ni lo necesita, y se ejecuta por separado.

**La pregunta que estudia.** El libro (Wackerly, Mendenhall y Scheaffer, *Estadística matemática con
aplicaciones*, 7.ª ed.) usa la distribución F para comparar dos varianzas: en el Ejemplo 7.7, en los
Ejercicios 7.27 y 7.36 y en el intervalo para σ₂²/σ₁² del Ejercicio 8.125. Todo eso descansa en que **las dos
poblaciones sean normales** (Teorema 7.3 y Definición 7.3). ¿Qué pasa si no lo son? La aplicación lo muestra
con simulación: qué eslabón de la teoría se rompe, cuánto se equivocan las probabilidades y los intervalos, qué
característica de la población decide el tamaño del error y por qué más datos no lo arreglan.

Hecha en Python con Streamlit, NumPy, SciPy, Plotly y pandas.

---

## 1. Instalación en Windows

### Opción A: Python de python.org (recomendada)

1. Instala **Python 3.10 o superior** desde <https://www.python.org/downloads/>. En la primera pantalla del
   instalador marca **«Add python.exe to PATH»**. (Si ya instalaste Python para la primera aplicación, no hace
   falta repetirlo.)
2. Descomprime la carpeta `laboratorio_f` donde quieras, por ejemplo en `Documentos`.
3. Doble clic en **`instalar_windows.bat`**. Crea un entorno virtual (`.venv`) e instala las librerías. Solo la
   primera vez; tarda unos minutos.
4. Doble clic en **`iniciar_windows.bat`**. Se abre el navegador en `http://localhost:8502`.
   Para cerrar, cierra la ventana negra.

Usa el puerto **8502** para que puedas tener abiertas a la vez esta aplicación y la de intervalos (que usa 8501).

Si Windows dice que no encuentra `python`, prueba `py --version` en el símbolo del sistema; si funciona, cambia
`python` por `py` dentro de los archivos `.bat`.

### Opción B: Anaconda

```bat
cd ruta\a\laboratorio_f
conda create -n laboratorio python=3.12 -y
conda activate laboratorio
pip install -r requirements.txt
streamlit run app.py --server.port 8502
```

Si ya creaste el entorno `laboratorio` para la primera aplicación, basta con `conda activate laboratorio`,
`pip install -r requirements.txt` y `streamlit run app.py --server.port 8502`.

La aplicación **no se ejecuta con el botón «Run» de Spyder**; se lanza con `streamlit run` desde la terminal.

### Comprobar que todo funciona

Doble clic en **`probar_windows.bat`** (o `python -m pytest -v`). Tarda unos minutos y deben pasar todas las
pruebas (ver `docs/04_validacion.md`).

---

## 2. Qué hay en la aplicación

| Página | Qué se ve |
|---|---|
| **Inicio** | Eliges la forma de las dos poblaciones y n; en vivo se simulan 20 000 pares de muestras, se dibuja F* sobre la F del libro, se ilumina la cadena de resultados y se muestra la cobertura real del intervalo del 95 %. |
| **Fundamentos** | Teorema 7.3, Definición 7.3, propiedades de la F (Ejercicios 7.29, 7.31, 7.33, 7.34), el intervalo del Ejercicio 8.125 por el método del pivote y por qué importa la normalidad. |
| **1. Construye tu F** | Dos poblaciones con forma, σ, μ y n propios; histograma de F* contra F(n₁−1, n₂−1); probabilidades de cola prometidas frente a simuladas; media, varianza y distancia KS; anatomía de un par de muestras. |
| **2. Dónde se rompe la cadena** | Eslabón por eslabón: E(S²) = σ² (siempre), V(S²) (solo con normalidad es 2σ⁴/(n−1)), W = (n−1)S²/σ² frente a χ², y F* frente a F. |
| **3. ¿Se cumple lo que promete la F?** | Las probabilidades del Ejemplo 7.7 y del Ejercicio 7.27 con la F y con la simulación; cómo cambia el error con n. |
| **4. El intervalo para σ₂²/σ₁²** | Miles de intervalos del Ejercicio 8.125 dibujados; cobertura real; cobertura según n; por qué es el mismo problema que la F. |
| **5. Mapa de robustez** | 14 distribuciones ordenadas por su curtosis caen sobre una sola curva; mapa de calor con 49 parejas de formas. |
| **6. Experimentos guiados** | Seis preguntas para predecir y comprobar: la media, asimetría frente a colas, una sola población no normal, n grande, colas livianas, casi normal. |
| **Calculadora** | Ejemplo 7.7 y Ejercicios 7.27, 7.36 y 8.126 paso a paso; cuantiles y probabilidades; intervalo con tus propios datos. |
| **Correspondencia** | Qué parte de la aplicación usa qué resultado del libro, y qué es complementario. |

Las poblaciones disponibles son normal, uniforme, t de Student, exponencial, gamma y log-normal. Todas se
estandarizan a media 0 y varianza 1 y luego se escalan, Y = μ + σX, así que σ² es exactamente la varianza de
la población y lo único que cambia entre escenarios es la **forma**.

---

## 3. Estructura del proyecto

```
laboratorio_f/
├── app.py                    Menú de navegación
├── requirements.txt
├── instalar_windows.bat / iniciar_windows.bat / probar_windows.bat
├── .streamlit/config.toml    Tema visual
├── nucleo/                   Matemática y simulación (sin interfaz)
│   ├── poblaciones.py        Formas estandarizadas, curtosis, asimetría, densidades
│   ├── fdist.py              Cuantiles de la F, intervalo central, intervalo del Ejercicio 8.125
│   ├── motor.py              Monte Carlo por lotes de S₁², S₂², W₁, W₂ y F*; coberturas y colas
│   ├── teoria.py             Momentos de la F y resultados complementarios (marcados como tales)
│   ├── ejemplos.py           Ejemplos y ejercicios del libro con sus resultados impresos
│   ├── graficos.py           Gráficos Plotly
│   └── ui.py                 Componentes de interfaz, caché y estado
├── paginas/                  Una página por archivo
├── tests/                    Pruebas (libro, simulación, interfaz)
└── docs/
    ├── 01_documento_matematico.md
    ├── 02_guion_sustentacion.md
    ├── 03_preguntas_dificiles.md
    └── 04_validacion.md
```

## 4. Detalles computacionales

- **Memoria acotada.** Las muestras se generan por lotes de a lo sumo 4 millones de números y se descartan;
  solo se guardan S₁² y S₂² de cada réplica. Límites: n ≤ 20 000, B ≤ 200 000 y B·(n₁ + n₂) ≤ 300 millones.
- **Reproducibilidad.** Cada población tiene su propio generador derivado de la semilla (`SeedSequence.spawn`),
  así que las muestras son independientes y el resultado no depende del tamaño del lote.
- **Sin recálculos innecesarios.** Las simulaciones solo corren al pulsar el botón y se guardan en caché; si
  cambias un control, la página avisa de que el resultado mostrado es del escenario anterior.
- **Exportación.** Cada gráfico se descarga como PNG (ícono de cámara) o como HTML interactivo; cada tabla,
  como CSV.
