import numpy as np
import streamlit as st
from scipy import stats

from nucleo import estado
from nucleo import excel as xl
from nucleo import graficos as gr
from nucleo import pruebaz as pz
from nucleo import signos as sg
from nucleo import ui
from nucleo.ui import ALFA, BETA, NAVY, POTENCIA

ui.preparar()
ss = st.session_state
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

ui.encabezado(
    "Excel: compruébalo y trae tus datos",
    "Tres formas de meter Excel en la exposición: el profesor recalcula todo con fórmulas de Excel, se prueban "
    "datos reales que vienen en una hoja de cálculo, y la configuración se edita en Excel y vuelve a la app.",
    "Las fórmulas del libro de Excel son las mismas de la Sección 10.2 (binomial) y de la Sección 10.4 "
    "(prueba Z y tamaño de muestra).")

t1, t2, t3 = st.tabs(["1. Llévalo a Excel", "2. Prueba con tus datos", "3. Trae tu configuración"])

# ------------------------------------------------------------------------------------------------ 1
with t1:
    st.markdown(
        "El libro **no trae números pegados**: cada resultado es una fórmula de Excel "
        "(`BINOMDIST`, `NORMSINV`, `NORMDIST`, `COUNTIFS`). Cambias una celda amarilla y Excel recalcula. "
        "Así se comprueba la app con una herramienta independiente.")
    c1, c2 = st.columns([1.3, 1], gap="large")
    with c1:
        st.markdown(
            "| Hoja | Qué tiene |\n|---|---|\n"
            "| **Binomial** | El ejemplo de Jones con tus valores del Módulo 1: tabla de probabilidades, región de rechazo, α, β y potencia, con gráfico. |\n"
            "| **Curva_beta** | β(p) y potencia para p = .01, …, .99: toda la alternativa compuesta. |\n"
            "| **Prueba_Z** | Tus valores del Módulo 2: EE, z_α, frontera k, α, β, potencia, n requerido y una celda para mover k a mano. |\n"
            "| **Monte_Carlo** | Si simulaste la prueba Z en el Módulo 3: las medias simuladas; Excel vuelve a aplicar la regla y cuenta los errores. |\n"
            "| **Tus_datos** | Plantilla: pegas una columna de datos y Excel hace la prueba Z. |")
    with c2:
        okb, msgb = estado.binom_valida()
        okz, msgz = estado.z_valida()
        mc_res = ss.get("mc_res")
        usa_mc = mc_res is not None and "media_muestral" in mc_res["df"].columns
        if not (okb and okz):
            st.error(msgb or msgz)
        else:
            cfg = estado.config_z()
            mc_df = mc_res["df"] if usa_mc and mc_res["params"] == pz.como_dict(cfg) else None
            if usa_mc and mc_df is None:
                st.caption("Cambiaste la prueba Z después de simular: la hoja Monte_Carlo no se incluye "
                           "hasta que vuelvas a simular.")
            elif mc_df is not None:
                st.caption(f"Incluye {min(len(mc_df), xl.MC_MAX_FILAS):,} experimentos del Módulo 3.".replace(",", "."))
            else:
                st.caption("Para incluir la hoja Monte_Carlo, simula la prueba Z en el Módulo 3.")
            if st.button("Preparar el libro de Excel", type="primary", width="stretch"):
                with st.spinner("Escribiendo fórmulas…"):
                    ss.x_libro = xl.construir_libro(estado.binom(), cfg, float(ss.z_beta_obj), mc=mc_df)
            if "x_libro" in ss:
                st.download_button("Descargar laboratorio_errores.xlsx", ss.x_libro, "laboratorio_errores.xlsx",
                                   mime=XLSX, width="stretch")
    st.subheader("Qué comprobar en Excel durante la exposición")
    st.markdown(
        "1. Hoja **Binomial** con n = 15, p₀ = 0.5, p₁ = 0.3, c = 2: α = 0.00369, β = 0.873, potencia = 0.127.\n"
        "2. Cambiar **c a 5** (la otra región que compara el libro): α sube a 0.151 y β baja a 0.278.\n"
        "3. Hoja **Prueba_Z**: mover el **k propuesto** (celda E4) y ver α(k) y β(k) moverse en sentido contrario.\n"
        "4. Hoja **Monte_Carlo**: la frecuencia de error que cuenta Excel con `COUNTIFS` es la misma de la app.\n"
        "5. Subir el libro editado en la pestaña 3 para que la app use los valores cambiados en Excel.")
    st.caption("En Excel en español las funciones se ven como DISTR.BINOM, DISTR.NORM.ESTAND.INV, DISTR.NORM y "
               "CONTAR.SI.CONJUNTO; Excel las traduce solo.")


# ------------------------------------------------------------------------------------------------ 2
def _al_subir_datos():
    archivo = ss.get("x_archivo")
    ss.pop("x_res", None)
    ss.pop("x_col", None)
    if archivo is None:
        return
    try:
        contenido = archivo.getvalue()
        res = xl.leer_csv(contenido) if archivo.name.lower().endswith(".csv") else xl.leer(contenido)
    except Exception as e:  # noqa: BLE001
        ss.x_res = {"error": str(e)}
        return
    ss.x_res = res
    cfg = estado.config_z() if estado.z_valida()[0] else pz.ConfigZ()
    p = res.get("params_datos", {"mu0": cfg.mu0, "sigma": cfg.sigma, "alfa": cfg.alfa, "cola": cfg.cola})
    ss.x_mu0, ss.x_sigma, ss.x_alfa, ss.x_cola = float(p["mu0"]), float(p["sigma"]), float(p["alfa"]), p["cola"]
    if res.get("columnas"):
        ss.x_col = res["columnas"][0]


with t2:
    c1, c2 = st.columns([1, 2.2], gap="large")
    with c1:
        st.file_uploader("Sube un Excel (.xlsx) o un CSV con una columna de datos", type=["xlsx", "csv"],
                         key="x_archivo", on_change=_al_subir_datos)
        cfg_p = estado.config_z() if estado.z_valida()[0] else pz.ConfigZ()
        st.download_button("Descargar plantilla Tus_datos.xlsx", xl.plantilla(cfg_p), "plantilla_tus_datos.xlsx",
                           mime=XLSX, width="stretch")
        st.caption("Sirve cualquier hoja con una columna de números (por ejemplo una serie descargada del DANE o "
                   "del Banco de la República). Con la plantilla, la app lee también μ₀, σ, α y la cola.")
    res = ss.get("x_res")
    with c2:
        if res is None:
            st.info("Sube un archivo para hacer la prueba Z con datos reales. Si no tienes uno, descarga la "
                    "plantilla: trae datos de ejemplo.")
        elif "error" in res:
            st.error(res["error"])
        else:
            for a in res["avisos"]:
                st.caption(a)
            if len(res.get("columnas", [])) > 1:
                st.selectbox("Columna", res["columnas"], key="x_col")
            datos = xl.columna(res["tabla"], ss.x_col) if res.get("columnas") and "x_col" in ss else res.get("datos")
            if datos is None or len(datos) < 2:
                st.error("No hay al menos 2 observaciones numéricas.")
            else:
                p1, p2, p3, p4 = st.columns(4)
                p1.number_input("μ₀", step=0.1, format="%.4f", key="x_mu0")
                p2.number_input("σ conocida", min_value=1e-6, step=0.1, format="%.4f", key="x_sigma")
                p3.number_input("α", min_value=0.001, max_value=0.5, step=0.005, format="%.3f", key="x_alfa")
                p4.selectbox("Hₐ", pz.COLAS, key="x_cola",
                             format_func=lambda c: "μ > μ₀" if c == "superior" else "μ < μ₀")
                n = len(datos)
                ybar, s = float(np.mean(datos)), float(np.std(datos, ddof=1))
                cfg = pz.ConfigZ(float(ss.x_mu0), float(ss.x_mu0) + (1 if ss.x_cola == "superior" else -1),
                                 float(ss.x_sigma), n, float(ss.x_alfa), ss.x_cola)
                z = float(pz.estadistico(ybar, cfg))
                rechaza = bool(pz.rechaza_z(z, cfg))
                vp = pz.valor_p(z, cfg)
                ui.cifras([
                    ("n · ȳ · s", f"{ybar:.4f}", f"n = {n}, s = {s:.4f}", NAVY),
                    ("z = (ȳ − μ₀)/(σ/√n)", f"{z:.3f}", f"crítico {'' if ss.x_cola == 'superior' else '−'}"
                                                         f"{pz.z_cola(cfg.alfa):.3f}", NAVY),
                    ("Decisión", "Rechazar H₀" if rechaza else "No rechazar H₀", f"valor p = {vp:.4f}",
                     ALFA if rechaza else POTENCIA),
                ])
                st.plotly_chart(gr.histograma_datos(datos, cfg.mu0, ybar, "Tus datos"), width="stretch")
                if rechaza:
                    st.markdown(f"Si en realidad μ = {cfg.mu0:g}, esta decisión sería un **error tipo I**; la regla "
                                f"lo comete con probabilidad α = {cfg.alfa:g}.")
                else:
                    zc = estado.config_z() if estado.z_valida()[0] else None
                    texto = ""
                    if zc is not None and zc.cola == ss.x_cola and zc.mu0 == cfg.mu0:
                        cz = pz.ConfigZ(cfg.mu0, zc.mu1, cfg.sigma, n, cfg.alfa, cfg.cola)
                        texto = (f" Con estos n y σ, si el verdadero fuera μ₁ = {zc.mu1:g} (Módulo 2), "
                                 f"β = {pz.resumen(cz)['beta']:.4f}.")
                    st.markdown("No rechazar no prueba que H₀ sea cierta: si la alternativa es la verdadera, esta "
                                "decisión sería un **error tipo II**, cuya probabilidad depende del μ verdadero." + texto)
                if abs(s - cfg.sigma) > 0.25 * cfg.sigma:
                    st.warning(f"La desviación muestral s = {s:.3f} es muy distinta de la σ = {cfg.sigma:g} que "
                               "supusiste conocida. Revisa σ: la prueba Z de este módulo supone σ conocida.")
                try:
                    sp = sg.prueba(datos, cfg.mu0, cfg.alfa, ss.x_cola)
                except ValueError:
                    sp = None
                with st.expander("Y sin suponer normalidad: prueba de signos con m₀ = μ₀"):
                    if sp is None:
                        st.caption("Todas las observaciones son iguales a μ₀: no hay signos que contar.")
                    else:
                        st.markdown(
                            f"Signos +: **{sp['y']}** de {sp['n_usados']} (descartados por empate: {sp['empates']}). "
                            f"Región de rechazo con α exacto = {sp['alfa_real']:.4f}: "
                            f"y {'≥' if ss.x_cola == 'superior' else '≤'} {sp['c']}. Valor p = {sp['valor_p']:.4f} → "
                            f"**{'Rechazar H₀' if sp['rechaza'] else 'No rechazar H₀'}** (sobre la mediana).")
                        if abs(float(stats.skew(datos))) > 1:
                            st.caption("Los datos son bastante asimétricos: aquí la prueba de signos es la más segura.")


# ------------------------------------------------------------------------------------------------ 3
def _al_subir_cfg():
    archivo = ss.get("x_cfg_archivo")
    ss.pop("x_cfg", None)
    if archivo is None:
        return
    try:
        contenido = archivo.getvalue()
        if archivo.name.lower().endswith(".json"):
            ss.x_cfg = {"config_z": pz.de_json(contenido.decode("utf-8")), "avisos": []}
        else:
            ss.x_cfg = xl.leer(contenido)
    except Exception as e:  # noqa: BLE001
        ss.x_cfg = {"error": str(e)}


def _usar_cfg():
    r = ss.get("x_cfg") or {}
    if "config_z" in r:
        estado.aplicar_z(r["config_z"])
    if "binomial" in r:
        estado.aplicar_binom(r["binomial"])
    ss.pop("x_libro", None)
    ss.x_cfg_ok = True


with t3:
    st.markdown("Edita las celdas amarillas de las hojas **Binomial** y **Prueba_Z** en Excel, guarda y sube el "
                "libro aquí: la app toma esos valores en los Módulos 1 a 4. También acepta el JSON del Módulo 2.")
    st.file_uploader("Libro de Excel del laboratorio (.xlsx) o configuración (.json)", type=["xlsx", "json"],
                     key="x_cfg_archivo", on_change=_al_subir_cfg)
    r = ss.get("x_cfg")
    if r is not None:
        if "error" in r:
            st.error(r["error"])
        else:
            for a in r["avisos"]:
                st.caption(a)
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.subheader("Prueba Z")
                if "config_z" in r:
                    z = r["config_z"]
                    st.markdown(f"μ₀ = {z.mu0:g}, μ₁ = {z.mu1:g}, σ = {z.sigma:g}, n = {z.n}, α = {z.alfa:g}, "
                                f"{'Hₐ: μ > μ₀' if z.cola == 'superior' else 'Hₐ: μ < μ₀'}")
                    rz = pz.resumen(z)
                    st.caption(f"Con esto: k = {rz['k']:.4f}, β = {rz['beta']:.4f}, potencia = {rz['potencia']:.4f}")
                else:
                    st.caption("No encontré una hoja Prueba_Z válida.")
            with c2:
                st.subheader("Binomial")
                if "binomial" in r:
                    b = r["binomial"]
                    st.markdown(f"n = {b['n']}, p₀ = {b['p0']:g}, p₁ = {b['p1']:g}, "
                                f"RR = {{y {'≤' if b['cola'] == 'inferior' else '≥'} {b['c']}}}")
                else:
                    st.caption("No encontré una hoja Binomial válida.")
            if "config_z" in r or "binomial" in r:
                st.button("Usar estos valores en la app", type="primary", on_click=_usar_cfg)
    if ss.pop("x_cfg_ok", False):
        st.success("Listo: los módulos ya usan los valores del archivo.")
        ui.enlace("paginas/m1_binomial.py", "Ir al Módulo 1")
        ui.enlace("paginas/m2_dilema.py", "Ir al Módulo 2")
