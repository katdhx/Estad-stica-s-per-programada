import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

from lab import graficos as gr
from lab import motor, sustitucion, ui
from lab.procedimientos import DOS_MUESTRAS, PROPORCION, UNA_MUESTRA

P = "e1"
ui.preparar()
ui.encabezado(
    "Experimento 1. Construcción de intervalos",
    "¿Qué significa «95 % de confianza»? Se generan B muestras, cada una produce su intervalo, y se ve cuáles "
    "contienen el verdadero parámetro. La confianza es una propiedad del procedimiento, no de un intervalo particular.",
    "Sección 8.5 (p. 406–407), Sección 8.6 y Figura 8.8 (p. 414–415), Ejercicios 8.51–8.53 (p. 416–417).",
)

esc, errores = ui.selector_escenario(P, n_defecto=20, B_defecto=100, B_max=5000, proc_defecto="media_t")
ui.costo(esc)
bloqueado = ui.mostrar_errores(errores)
if ui.boton_ejecutar(P, bloqueado):
    barra, avance = ui.barra_progreso()
    res = ui.simular_cache(esc, avance)
    barra.empty()
    ui.guardar(P, esc, res)

res, viejo = ui.recuperar(P, esc)
if res is None:
    st.info("Elige el escenario en la barra lateral y pulsa «Ejecutar simulación». Para reproducir la Figura 8.8, "
            "elige «Proporción p», p = 0.5, n = 35 y B = 24.")
    ui.ficha(esc.proc)
    st.stop()
if viejo:
    ui.aviso_desactualizado()

E = res.escenario
proc = E.proc
tabla = res.tabla
cob = res.cobertura()
fallas = cob.B - cob.aciertos

pres, fund, datos = st.tabs(["Resultados", "Fundamentación matemática", "Datos y descargas"])

with pres:
    c = st.columns(4)
    c[0].metric("Parámetro verdadero", f"{ui.fmt(res.theta)}")
    c[1].metric(f"Contienen el parámetro ({cob.estimada:.1%})", f"{cob.aciertos} de {cob.B}")
    c[2].metric("Nivel nominal 1 − α", f"{1 - E.alfa:.1%}")
    amp = tabla["amplitud"].to_numpy()
    c[3].metric("Amplitud media", ui.fmt(float(np.mean(amp))) if np.isfinite(amp).all() else "∞ (unilateral)")
    ui.veredicto(f"<b>{proc.calidad(E.pob1, E.pob2)}</b> Se esperaban unos {E.alfa * cob.B:.1f} intervalos "
                 f"que no contienen el parámetro, y hubo {fallas}.")

    mostrar = st.slider("Intervalos visibles", 10, 200, min(100, cob.B), 10, key=f"{P}_vis") if cob.B > 10 else cob.B
    inicio = 1
    if cob.B > mostrar:
        inicio = st.slider("Desde la muestra número", 1, cob.B - mostrar + 1, 1, key=f"{P}_ini")
    sel = tabla.iloc[inicio - 1: inicio - 1 + mostrar]
    k = st.number_input("Inspeccionar la muestra número", 1, cob.B, int(inicio), key=f"{P}_k")
    fig = gr.intervalos_apilados(sel, res.theta, ui.SIMBOLO[proc.clave],
                                 resaltar=int(k) if inicio <= k < inicio + mostrar else None,
                                 titulo=f"{proc.nombre}: muestras {inicio} a {inicio + len(sel) - 1}")
    ui.mostrar_figura(fig, "experimento1_intervalos", P)

    st.subheader(f"Muestra número {int(k)}")
    fila = tabla.iloc[int(k) - 1]
    est_k = {key: (val[int(k) - 1] if isinstance(val, np.ndarray) else val) for key, val in res.estadisticos.items()}
    cA, cB = st.columns([3, 2])
    with cA:
        sigma = E.pob1.desviacion() if proc.clave == "media_z_sigma" else None
        for linea in sustitucion.lineas(proc.clave, est_k, E.alfa, E.lado, sigma):
            st.latex(linea)
        if fila["cubre"]:
            st.success(f"Este intervalo contiene el valor verdadero {ui.fmt(res.theta)}.")
        else:
            st.warning(f"Este intervalo no contiene el valor verdadero {ui.fmt(res.theta)}. Le tocó la parte del "
                       f"{E.alfa:.0%} de muestras «desafortunadas».")
    with cB:
        if proc.familia in (UNA_MUESTRA, DOS_MUESTRAS):
            datos_k = motor.muestra_individual(E, int(k))
            y1 = datos_k["y1"]
            st.markdown(f"**Observaciones de la muestra** (n = {ui.entero(y1.size)})")
            vista = pd.DataFrame({"y": y1[:200]})
            if "y2" in datos_k:
                y2 = datos_k["y2"]
                vista = pd.DataFrame({"y₁": pd.Series(y1[:200]), "y₂": pd.Series(y2[:200])})
            st.dataframe(vista, height=240, use_container_width=True)
            if y1.size > 200:
                ui.nota(f"Se muestran las primeras 200 de {ui.entero(y1.size)} observaciones; los estadísticos usan todas.")
            ui.nota(f"Comprobación: el promedio recalculado es {y1.mean():.6f} y el usado en el intervalo es "
                    f"{est_k.get('media', est_k.get('media1', np.nan)):.6f}.")
        else:
            ui.nota("En proporciones se generó directamente el número de éxitos Y ~ Binomial(n, p), que es "
                    "la suma de los n ensayos de Bernoulli (Sección 7.5).")

    st.subheader("Proporción acumulada de intervalos que cubren")
    ui.mostrar_figura(gr.cobertura_acumulada(tabla["cubre"].to_numpy(), 1 - E.alfa), "experimento1_cobertura_acumulada", f"{P}_acum")
    ui.nota("La proporción oscila mucho al principio y se estabiliza alrededor del nivel nominal. La banda "
            "gris es 1 − α ± 1.96√(α(1 − α)/k): el rango en el que debería moverse si el procedimiento tiene "
            "exactamente el coeficiente 1 − α.")

with fund:
    st.markdown(r"""
**Por qué algunos intervalos fallan.** El parámetro $\theta$ es fijo; lo aleatorio son los extremos $\hat\theta_L$ y $\hat\theta_U$.
Para cada muestra, el evento «el intervalo contiene a $\theta$» tiene probabilidad $1-\alpha$ (Sección 8.5). Una vez observada
la muestra, el intervalo numérico contiene o no contiene a $\theta$: ya no hay probabilidad de por medio (p. 414–415).

**Cuántos fallan.** Las $B$ muestras son independientes, de modo que el número de intervalos que **no** contienen a $\theta$ es
$$F\sim\text{Binomial}(B,\ \alpha),\qquad E(F)=B\alpha,\qquad \sigma_F=\sqrt{B\alpha(1-\alpha)}.$$
""")
    pF = stats.binom(cob.B, E.alfa)
    st.markdown(
        f"Con B = {cob.B} y α = {E.alfa:g}: E(F) = {cob.B * E.alfa:.2f} y σ_F = {np.sqrt(cob.B * E.alfa * (1 - E.alfa)):.2f}. "
        f"Se observaron F = {fallas} fallas. Si el coeficiente real fuera exactamente 1 − α, la probabilidad de observar "
        f"{fallas} o más fallas sería {pF.sf(fallas - 1):.3f}, y la de observar {fallas} o menos, {pF.cdf(fallas):.3f}."
    )
    st.markdown(
        "En la Figura 8.8 del libro (B = 24, α = .05) se esperaba 1.2 fallas y se observó 1: el 95.8 % que reporta el "
        "texto es perfectamente compatible con el 95 % nominal."
    )
    ui.ficha(proc, expandida=True)

with datos:
    st.dataframe(tabla, use_container_width=True, height=360)
    ui.descargar_tabla(tabla, "experimento1_intervalos", P, ui.metadatos(E))
    st.download_button("Descargar configuración del experimento (JSON)", ui.configuracion_json(E),
                       file_name="experimento1_configuracion.json", mime="application/json", key=f"{P}_json")
    ui.nota(f"Tiempo de cálculo: {res.segundos:.2f} s. Con la misma semilla ({E.semilla}) se obtiene exactamente esta tabla.")
