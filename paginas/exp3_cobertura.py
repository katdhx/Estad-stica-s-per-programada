import numpy as np
import pandas as pd
import streamlit as st

from lab import graficos as gr
from lab import intervalos as ic
from lab import motor, teoria, ui
from lab.procedimientos import PROCEDIMIENTOS, UNA_MUESTRA

P = "e3"
ui.preparar()
ui.encabezado(
    "Experimento 3. Cobertura",
    "¿Con qué frecuencia contiene el intervalo al parámetro? La cobertura empírica se compara con el nivel nominal, "
    "y se mide también el error de la propia simulación, que es otra estimación de una proporción.",
    "Sección 8.5 (coeficiente de confianza, p. 406), Tabla 8.1 y Sección 8.6 (error estándar de una proporción), "
    "Ejercicios 8.52–8.55 (p. 416–417).",
)

esc, errores = ui.selector_escenario(P, n_defecto=10, B_defecto=10000, B_max=motor.B_MAXIMO,
                                     proc_defecto="media_t", pob_defecto="exponencial")
ui.costo(esc)
comparar = []
if esc.proc.familia == UNA_MUESTRA:
    candidatos = [k for k, p in PROCEDIMIENTOS.items()
                  if p.familia == UNA_MUESTRA and esc.pob1.clave in p.poblaciones and p.clave != "varianza_chi2"
                  and (p.clave != "media_z_sigma" or esc.pob1.varianza_finita())]
    comparar = st.sidebar.multiselect("Comparar sobre las mismas muestras", candidatos,
                                      default=[c for c in candidatos if c != esc.procedimiento][:3],
                                      format_func=lambda k: PROCEDIMIENTOS[k].nombre_corto, key=f"{P}_comp")
bloqueado = ui.mostrar_errores(errores)
if ui.boton_ejecutar(P, bloqueado):
    barra, avance = ui.barra_progreso()
    res = ui.simular_cache(esc, avance)
    barra.empty()
    ui.guardar(P, (esc, tuple(comparar)), (res, tuple(comparar)))

guardado, viejo = ui.recuperar(P, (esc, tuple(comparar)))
t_una, t_curva, t_porque, t_fund = st.tabs(
    ["Un escenario", "Cobertura en función de n", "¿Por qué no da exactamente 1 − α?", "Fundamentación matemática"]
)

with t_una:
    if guardado is None:
        st.info("Pulsa «Ejecutar simulación». Sugerencia: población exponencial con n = 10 y B = 10 000 para comparar "
                "un procedimiento exacto (pivote 2ΣY/θ) con los aproximados (Z y t).")
    else:
        if viejo:
            ui.aviso_desactualizado()
        res, comp = guardado
        E = res.escenario
        cob = res.cobertura()
        L95, U95 = cob.intervalo()
        c = st.columns(4)
        c[0].metric("Cobertura empírica ĉ", f"{cob.estimada:.4f}")
        c[1].metric("Nominal 1 − α", f"{cob.nominal:.4f}")
        c[2].metric("Error estándar Monte Carlo", f"{cob.error_estandar:.4f}")
        c[3].metric("Distancia en errores estándar", f"{cob.z_desviacion():+.2f}")
        compatible = cob.compatible_con_nominal()
        ui.veredicto(
            f"IC del 95 % para la cobertura real: <b>[{L95:.4f}, {U95:.4f}]</b>. "
            + ("La diferencia con el nivel nominal es compatible con el error de Monte Carlo: los datos simulados no "
               "contradicen que el coeficiente real sea 1 − α."
               if compatible else
               "La diferencia con el nivel nominal es <b>mayor que la que explica el error de Monte Carlo</b> "
               "(más de 1.96 errores estándar): el coeficiente real de este procedimiento, en este escenario, no es 1 − α.")
            + f"<br>{E.proc.calidad(E.pob1, E.pob2)}"
        )
        ui.mostrar_figura(gr.cobertura_acumulada(res.tabla["cubre"].to_numpy(), cob.nominal,
                                                 "Convergencia de la cobertura empírica"), "experimento3_convergencia", f"{P}_conv")

        if comp:
            st.subheader("Los mismos datos, distintos procedimientos")
            claves = [E.procedimiento] + [k for k in comp if k != E.procedimiento]
            filas = []
            for k in claves:
                t = motor.calcular_intervalos(E, res.estadisticos, procedimiento=k)
                cb = motor.resumen_cobertura(t["cubre"].to_numpy(), cob.nominal)
                filas.append({"procedimiento": PROCEDIMIENTOS[k].nombre_corto, "cobertura": cb.estimada,
                              "ee": cb.error_estandar, "amplitud media": float(t["amplitud"].replace(np.inf, np.nan).mean()),
                              "tipo": PROCEDIMIENTOS[k].calidad(E.pob1).split(":")[0]})
            dfc = pd.DataFrame(filas)
            fig = gr.barras_comparacion(dfc["procedimiento"].tolist(), dfc["cobertura"].tolist(), cob.nominal,
                                        "Cobertura empírica de cada procedimiento", "Cobertura",
                                        (1.96 * dfc["ee"]).tolist(), f"nominal {cob.nominal:.0%}")
            lo = max(0, min(dfc["cobertura"].min() - 0.05, cob.nominal - 0.05))
            fig.update_yaxes(range=[lo, 1.0])
            ui.mostrar_figura(fig, "experimento3_comparacion", f"{P}_bar")
            st.dataframe(dfc.style.format({"cobertura": "{:.4f}", "ee": "{:.4f}", "amplitud media": "{:.4f}"}),
                         use_container_width=True, hide_index=True)
            ui.nota("Todos se calculan con las mismas B muestras, así que las diferencias se deben al procedimiento, "
                    "no al azar del muestreo.")
        ui.descargar_tabla(res.tabla, "experimento3_intervalos", P, ui.metadatos(E))

with t_curva:
    st.markdown("Para cada n se simulan B muestras nuevas y se calcula la cobertura de los procedimientos elegidos "
                "con esas mismas muestras.")
    ns_opc = [2, 3, 5, 8, 10, 15, 20, 30, 50, 100, 200, 500, 1000]
    c1, c2 = st.columns([3, 1])
    ns = c1.multiselect("Valores de n", ns_opc, default=[3, 5, 10, 20, 30, 50, 100, 500], key=f"{P}_ns")
    Bc = int(c2.number_input("B por cada n", 100, 50000, 4000, step=500, key=f"{P}_Bc"))
    procs = tuple(dict.fromkeys([esc.procedimiento] + list(comparar)))
    minimo = 2
    ns = sorted(n for n in ns if n >= minimo)
    if st.button("Calcular la curva de cobertura", type="primary", disabled=bool(errores) or not ns, key=f"{P}_curva"):
        esc_b = motor.Escenario(esc.procedimiento, esc.pob1, esc.n1, Bc, esc.alfa, esc.lado, esc.semilla, esc.pob2, esc.n2)
        barra, avance = ui.barra_progreso("Calculando la cobertura para cada n…")
        df = ui.barrido_cache(esc_b, tuple(ns), procs, None, avance)
        barra.empty()
        st.session_state[f"{P}_curva_res"] = (esc_b, df)
    if f"{P}_curva_res" in st.session_state:
        esc_b, df = st.session_state[f"{P}_curva_res"]
        etiquetas = {k: PROCEDIMIENTOS[k].nombre_corto for k in df["procedimiento"].unique()}
        teo = {}
        if esc_b.pob1.espec.es_normal and "media_z_s" in etiquetas:
            xs = np.array(sorted(df["n"].unique()))
            teo["media_z_s"] = (xs, np.array([teoria.cobertura_exacta_z_s_normal(int(n), esc_b.alfa) for n in xs]))
        fig = gr.curva_vs_n(df, "cobertura", etiquetas, f"Cobertura según n ({esc_b.pob1.descripcion_corta()})",
                            y="Cobertura", nominal=1 - esc_b.alfa, columna_error="ee_cobertura", B=esc_b.B,
                            teorico=teo or None)
        ui.mostrar_figura(fig, "experimento3_cobertura_vs_n", f"{P}_cvn")
        if teo:
            ui.nota("Curva teórica (complementaria): bajo normalidad, la cobertura exacta de Ȳ ± z S/√n es "
                    "P(|T| ≤ z_{α/2}) con T ~ t(n − 1), que es menor que 1 − α y tiende a ella al crecer n.")
        st.dataframe(df, use_container_width=True, hide_index=True)
        ui.descargar_tabla(df, "experimento3_cobertura_vs_n", f"{P}_cvn")

with t_porque:
    st.markdown(r"""
Hay **cuatro** razones distintas por las que la cobertura empírica $\hat c$ no coincide exactamente con $1-\alpha$.
Distinguirlas es la parte importante.

**1. Error de Monte Carlo (siempre presente).** Cada intervalo cubre o no cubre: es un ensayo de Bernoulli con
probabilidad $c$ (la cobertura real). Las $B$ réplicas son independientes, así que el número de aciertos es
Binomial$(B,c)$ y $\hat c$ es una proporción muestral. Por la Tabla 8.1:
$$E(\hat c)=c,\qquad \sigma_{\hat c}=\sqrt{\frac{c(1-c)}{B}}.$$
Aunque el procedimiento sea exacto ($c=1-\alpha$), $\hat c$ fluctúa. Con $B=10\,000$ y $c=.95$, $\sigma_{\hat c}=.0022$,
así que $\hat c=.9478$ es perfectamente normal. El intervalo para $c$ que muestra la app es el de la Sección 8.6:
$\hat c\pm1.96\sqrt{\hat c(1-\hat c)/B}$.

**2. Procedimiento aproximado (asintótico).** Si el pivote solo es aproximadamente normal (TCL), entonces
$c=c(n)\neq1-\alpha$ para $n$ finito, aunque $c(n)\to1-\alpha$. Ejemplo: $\bar Y\pm z_{\alpha/2}S/\sqrt n$ con $n=5$.

**3. Supuestos violados.** Si se usa un resultado exacto fuera de sus hipótesis, la cobertura real puede ser distinta y
**no** acercarse a $1-\alpha$ con $n$ grande. Ejemplo: χ² para $\sigma^2$ con población exponencial (Experimento 6).

**4. Discreción.** Con datos binomiales, $\hat p$ solo toma $n+1$ valores, y la cobertura exacta oscila con $p$ y $n$
(Experimento 6).

**¿Cuántas réplicas hacen falta?** Es otra vez la Sección 8.7. Para estimar $c$ con error menor que $E$ con
probabilidad .95, se necesita
$$B=\frac{1.96^2\,c(1-c)}{E^2}.$$
""")
    tabla_B = pd.DataFrame({"E (precisión deseada)": [0.01, 0.005, 0.002, 0.001]})
    tabla_B["B necesario (c = 0.95)"] = [int(np.ceil(1.96**2 * 0.95 * 0.05 / e**2)) for e in tabla_B.iloc[:, 0]]
    st.dataframe(tabla_B, hide_index=True)
    ui.nota("Por eso la Figura 8.8 del libro (B = 24) no permite distinguir 95 % de 90 %: con B = 24, σ_ĉ ≈ 0.044.")

with t_fund:
    st.markdown(r"""
**Definición que se pone a prueba.** El coeficiente de confianza es $P(\hat\theta_L\le\theta\le\hat\theta_U)$ (Sección 8.5),
«la fracción de veces, en muestreo repetido, que los intervalos construidos contienen al parámetro objetivo».
La simulación construye literalmente ese muestreo repetido.

**Ley de los grandes números, en la versión que usamos.** $\hat c$ es insesgado y $V(\hat c)=c(1-c)/B\to0$.
Por Tchebysheff (Sección 4.10), $P(|\hat c-c|\ge k\sigma_{\hat c})\le1/k^2$, de modo que $\hat c\to c$. La gráfica de convergencia lo muestra.

**Contraste.** El valor «distancia en errores estándar» es $(\hat c-(1-\alpha))/\sqrt{(1-\alpha)\alpha/B}$.
Si el coeficiente real fuera $1-\alpha$, por el TCL sería aproximadamente $N(0,1)$. Un valor mayor que 1.96 en valor absoluto
indica que el procedimiento no tiene el coeficiente nominal en ese escenario. Es la idea del Ejemplo 7.8 (p. 372),
que el libro llama «comprobación de hipótesis».

**Demostración frente a comprobación.** Que la t con población normal dé $\hat c\approx.95$ **no demuestra** el Teorema 7.3:
lo ilustra para un $n$, un $\sigma$ y una semilla. La demostración es la de la Sección 7.2. Lo que la simulación sí puede
hacer es **refutar** una afirmación de exactitud, como ocurre con la χ² fuera de la normalidad.
""")
    ui.ficha(esc.proc)
