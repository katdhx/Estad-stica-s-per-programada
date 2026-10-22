# Laboratorio de intervalos de confianza

Aplicación interactiva para estudiar experimentalmente los intervalos de confianza de los capítulos 7 y 8 de
Wackerly, Mendenhall y Scheaffer, *Estadística matemática con aplicaciones*, 7.ª edición.

Está hecha en Python con Streamlit (interfaz), NumPy (simulación), SciPy (distribuciones), Plotly (gráficos) y
pandas (tablas).

---

## 1. Instalación en Windows

### Opción A: Python de python.org (recomendada)

1. Instala **Python 3.10 o superior** desde <https://www.python.org/downloads/>.
   En la primera pantalla del instalador marca **«Add python.exe to PATH»**.
2. Descomprime la carpeta `laboratorio_ic` donde quieras, por ejemplo en `Documentos`.
3. Haz doble clic en **`instalar_windows.bat`**. Crea un entorno virtual (`.venv`) e instala las librerías.
   Solo hace falta la primera vez y tarda unos minutos.
4. Haz doble clic en **`iniciar_windows.bat`**. Se abre el navegador en `http://localhost:8501`.
   Para cerrar la aplicación, cierra la ventana negra (o pulsa `Ctrl + C` en ella).

Si Windows dice que no encuentra `python`, abre el símbolo del sistema y prueba `py --version`. Si eso funciona,
edita los archivos `.bat` y cambia `python` por `py`.

### Opción B: Anaconda (si ya usas Spyder)

Abre **Anaconda Prompt** y escribe:

```bat
cd ruta\a\laboratorio_ic
conda create -n laboratorio python=3.12 -y
conda activate laboratorio
pip install -r requirements.txt
streamlit run app.py
```

Las veces siguientes basta con:

```bat
conda activate laboratorio
cd ruta\a\laboratorio_ic
streamlit run app.py
```

La aplicación **no se ejecuta con el botón «Run» de Spyder**. Hay que lanzarla con `streamlit run app.py` desde
la terminal. Spyder sirve para leer y modificar el código.

### Comprobar que todo funciona

Haz doble clic en **`probar_windows.bat`** (o ejecuta `python -m pytest -v`). Deben pasar todas las pruebas.
Entre ellas están la reproducción de los ejemplos numéricos del libro, la comparación de los valores críticos con
las tablas del Apéndice 3 y las pruebas estadísticas del motor de simulación.

### Para la sustentación

- Abre la aplicación **antes** de entrar y deja cargada la página de Inicio.
- La aplicación funciona sin internet. Sin conexión, las fuentes tipográficas se sustituyen por las del sistema y
  el botón «Descargar gráfico interactivo (HTML)» genera archivos que necesitan internet para abrirse después.
  La descarga PNG (ícono de cámara sobre cada gráfico) funciona siempre.
- Con la misma **semilla** se repite exactamente cada experimento.

---

## 2. Estructura del proyecto

```
laboratorio_ic/
├── app.py                     Punto de entrada y menú de navegación
├── requirements.txt
├── instalar_windows.bat       Crea el entorno e instala las librerías
├── iniciar_windows.bat        Abre la aplicación
├── probar_windows.bat         Ejecuta las pruebas
├── .streamlit/config.toml     Tema visual
├── lab/                       Núcleo matemático y computacional (sin interfaz)
│   ├── poblaciones.py         Distribuciones: normal, uniforme, exponencial, gamma, log-normal, t, dado, Bernoulli
│   ├── intervalos.py          Fórmulas de los intervalos (funciones puras y vectorizadas)
│   ├── procedimientos.py      Ficha matemática de cada procedimiento + su cálculo
│   ├── motor.py               Motor de Monte Carlo por lotes (memoria acotada, reproducible)
│   ├── teoria.py              Resultados teóricos para comparar (amplitudes, coberturas exactas)
│   ├── sustitucion.py         Escribe un intervalo con los números sustituidos (LaTeX)
│   ├── ejemplos_libro.py      Ejemplos 8.4, 8.7, 8.8, 8.11, 8.12, 8.13 con sus resultados impresos
│   ├── correspondencia.py     Tabla módulo ↔ libro
│   ├── graficos.py            Gráficos Plotly con la identidad visual del laboratorio
│   └── ui.py                  Componentes de interfaz compartidos (Streamlit)
├── paginas/                   Una página por experimento
├── tests/                     Pruebas con pytest
└── docs/                      Documento matemático, guion y preguntas de sustentación
```

## 3. Qué contiene la aplicación

| Página | Pregunta que responde |
|---|---|
| Inicio | La Figura 8.8 del libro en vivo; la diferencia entre n (tamaño de cada muestra) y B (número de muestras). |
| Fundamentos | Teoremas del capítulo 7, definiciones del 8, método del pivote y la ficha de cada procedimiento. |
| 1. Construcción | ¿Qué significa «95 % de confianza»? Muchos intervalos, inspección individual con la cuenta completa. |
| 2. Tamaño muestral | ¿Por qué la amplitud cae como 1/√n? De n = 5 a n = 100 000; una muestra que crece; cálculo de n. |
| 3. Cobertura | ¿Coincide la cobertura simulada con la nominal? Error de Monte Carlo; varios procedimientos con los mismos datos. |
| 4. Nivel de confianza | 90/95/99 % sobre las mismas muestras: el precio de la confianza. |
| 5. Distribuciones muestrales | Ȳ, (n−1)S²/σ², T, independencia de Ȳ y S², pivote ↔ cobertura, sesgo y MSE, binomial. |
| 6. Supuestos | χ² sin normalidad, t sin normalidad, proporciones extremas, t agrupada con varianzas distintas. |
| Calculadora | Ejemplos del libro reproducidos paso a paso; intervalos con datos propios; tablas de valores críticos. |
| Correspondencia | Tabla de cada módulo con su sección, teorema y página del libro. |

## 4. Límites computacionales

- n ≤ 100 000 observaciones por muestra; B ≤ 200 000 muestras; n × B ≤ 300 millones por simulación.
- Las muestras se generan por lotes de a lo sumo 4 millones de números (≈ 32 MB) y solo se guardan los estadísticos
  suficientes (media, varianza, suma). Así, 1000 muestras de 100 000 observaciones no saturan la memoria.
- Los resultados se guardan en caché: volver a ejecutar con los mismos controles es instantáneo.
