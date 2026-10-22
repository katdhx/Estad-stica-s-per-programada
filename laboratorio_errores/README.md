# El costo de equivocarse: errores tipo I y tipo II

Primera de las dos aplicaciones para la exposición del capítulo 10 de Wackerly, Mendenhall y Scheaffer,
*Estadística matemática con aplicaciones*, 7.ª edición: secciones **10.1** y **10.2**, con conexión a la **10.4**.
La segunda es «Del riesgo a la evidencia: potencia y tamaño muestral», que importa la configuración Z en JSON.

Es independiente de las otras dos aplicaciones de este repositorio (intervalos de confianza y Laboratorio F):
no las modifica ni las necesita.

Hecha en Python con Streamlit, NumPy, SciPy, Plotly, pandas y openpyxl (para Excel).

---

## 1. Instalación en Windows

### Opción A: Python de python.org (recomendada)

1. Instala **Python 3.10 o superior** desde <https://www.python.org/downloads/>. En la primera pantalla del
   instalador marca **«Add python.exe to PATH»**.
2. Descarga el repositorio (botón verde **Code → Download ZIP** en GitHub), descomprímelo y entra a la carpeta
   `laboratorio_errores`.
3. Doble clic en **`instalar_windows.bat`**: crea un entorno virtual (`.venv`) e instala las librerías.
   Solo la primera vez; tarda unos minutos.
4. Doble clic en **`iniciar_windows.bat`**. Se abre el navegador en `http://localhost:8503`.
   Para cerrar, cierra la ventana negra.

Usa el puerto **8503**, así puedes tenerla abierta al mismo tiempo que las otras aplicaciones (8501 y 8502).

Si Windows dice que no encuentra `python`, prueba `py --version` en el símbolo del sistema; si funciona,
cambia `python` por `py` dentro de los `.bat`.

### Opción B: Anaconda / línea de comandos

```bat
cd ruta\a\laboratorio_errores
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

> Ejecuta siempre con `streamlit run app.py`. Con `python app.py` la app no abre.

### Pruebas

Doble clic en **`probar_windows.bat`**, o `python -m pytest -v` dentro de la carpeta.

## 2. Publicarla en Streamlit Community Cloud

En <https://share.streamlit.io> → **Create app** → repositorio `katdhx/Estad-stica-s-per-programada`,
rama `main`, **Main file path: `laboratorio_errores/app.py`**. Streamlit toma el `requirements.txt` de esa misma
carpeta.

---

## 3. Qué hay en la aplicación

| Página | Qué hace |
|---|---|
| Inicio | Los cuatro elementos de una prueba, las definiciones de error tipo I, tipo II y potencia, y el caso del libro. |
| 1. El ejemplo de Jones | Binomial exacta: n, p₀, p₁, umbral c y cola. α, β y potencia en vivo; curva β(p) para toda la alternativa compuesta; tabla con todas las reglas posibles; comprobación por simulación. |
| 2. El dilema entre α y β | Prueba Z con σ conocida: μ₀, μ₁, σ, n, α, cola. Las dos campanas con las áreas α, β y potencia; frontera k fija por α o movida a mano; por qué α baja y β sube; tamaño de muestra (Sección 10.4); exportar e importar JSON. |
| 3. Monte Carlo | Hasta 50 000 experimentos: cada uno genera una muestra completa, calcula el estadístico, aplica la regla y clasifica el resultado. Teórico contra empírico, error Monte Carlo y estabilización de las frecuencias. |
| 4. Toma una decisión | El público decide; la app revela la regla, el estado verdadero y el tipo de error. Marcador acumulado. |
| Excel | Libro con fórmulas vivas para comprobar todo en Excel, prueba Z con datos propios (Excel o CSV) y carga de configuraciones editadas en Excel. |
| Opcional: prueba de signos | Extensión separada: la binomial de Jones como prueba exacta para la mediana sin suponer normalidad. |

Los parámetros son compartidos: lo que cambias en el Módulo 1 o 2 es lo que usan el Monte Carlo, el juego de
decisión y Excel.

### La interacción con Excel

1. **Llévalo a Excel.** El botón *Preparar el libro de Excel* genera `laboratorio_errores.xlsx` con las hojas
   `Binomial`, `Curva_beta`, `Prueba_Z`, `Monte_Carlo` (si simulaste la prueba Z) y `Tus_datos`. Ningún resultado
   está pegado: son fórmulas (`BINOMDIST`, `NORMSINV`, `NORMDIST`, `COUNTIFS`) que Excel recalcula al cambiar
   una celda amarilla. Se usan las funciones de compatibilidad para que abra sin errores en cualquier Excel y en
   LibreOffice; Excel en español las muestra traducidas (DISTR.BINOM, DISTR.NORM.ESTAND.INV, …).
2. **Prueba con tus datos.** Sube un `.xlsx` o un `.csv` con una columna de números (por ejemplo una serie del DANE
   o del Banco de la República; acepta punto y coma y coma decimal). La app hace la prueba Z, dice qué error se
   podría estar cometiendo y añade la prueba de signos como alternativa sin normalidad.
3. **Trae tu configuración.** Edita las celdas amarillas de `Binomial` y `Prueba_Z` en Excel, sube el libro y
   pulsa *Usar estos valores en la app*. También acepta el JSON del Módulo 2.

## 4. Archivos

```
laboratorio_errores/
├── app.py                  navegación
├── nucleo/                 matemática y utilidades (sin Streamlit, salvo estado.py y ui.py)
│   ├── binomial.py         α, β, potencia y curva β(p) exactos (ejemplo de Jones)
│   ├── pruebaz.py          prueba Z, frontera k, n requerido, JSON
│   ├── montecarlo.py       simulación de experimentos y clasificación de errores
│   ├── signos.py           prueba de signos (extensión)
│   ├── excel.py            libro de Excel con fórmulas y lectura de archivos subidos
│   ├── graficos.py         gráficos Plotly
│   ├── estado.py           parámetros compartidos entre páginas
│   └── ui.py               estilo y colores (α rojo, β azul, potencia verde)
├── paginas/                una página por módulo
├── tests/                  61 pruebas (libro, fórmulas, Excel e interfaz)
├── docs/
│   ├── 01_documento_matematico.md
│   ├── 02_guion_sustentacion.md
│   ├── 03_preguntas_dificiles.md
│   ├── 04_validacion.md
│   └── config_ejemplo_Z.json
└── *.bat                   instalar, iniciar y probar en Windows
```

## 5. Identidad visual común con la segunda aplicación

Fondo claro `#F8F9FA`, azul marino `#0A2540`, grises. **α `#C0392B`** (rojo), **β `#2980B9`** (azul),
**potencia `#27AE60`** (verde). Notación: H₀, Hₐ, α, β, p₀, p₁, μ₀, μ₁, σ, n, Ȳ, k.

El JSON exportado trae `mu0`, `mu1`, `sigma`, `n`, `alfa`, `tipo_prueba` y, por compatibilidad con el formato
anterior, `alpha`, `alternative` (`lower`/`upper`) y `crit`. La app lee los dos formatos.
