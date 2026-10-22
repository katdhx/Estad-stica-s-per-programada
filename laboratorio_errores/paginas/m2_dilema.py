import numpy as np
import streamlit as st

from nucleo import estado
from nucleo import graficos as gr
from nucleo import pruebaz as pz
from nucleo import ui
from nucleo.ui import ALFA, BETA, NAVY, POTENCIA

ui.preparar()
ss = st.session_state
MODOS = ("Fijo α y calculo la frontera", "Muevo la frontera k a mano")


def _al_cambiar_cola():
    ss.z_mu1 = float(2 * ss.z_mu0 - ss.z_mu1)   # reflejar μ1 al otro lado de μ0
    ss.pop("z_k", None)


def _cargar_json():
    archivo = ss.get("z_json")
    if archivo is None:
        return
    try:
        estado.aplicar_z(pz.de_json(archivo.getvalue().decode("utf-8")))
        ss["z_json_msg"] = ("ok", "Configuración cargada.")
    except Exception as e:  # noqa: BLE001
        ss["z_json_msg"] = ("error", f"No pude leer el JSON: {e}")


ui.encabezado(
    "Módulo 2 · El dilema entre α y β",
    "La misma pregunta con una variable continua: la media de una población normal con σ conocida. "
    "¿Qué pasa con cada error si movemos la frontera de rechazo?",
    "Sección 10.2 (α, β y región de rechazo) y Sección 10.4 (cálculo de β y del tamaño de muestra para la "
    "prueba Z: n = (z_α + z_β)² σ² / (μₐ − μ₀)²).")

col_c, col_g = st.columns([1, 2.3], gap="large")
with col_c:
    st.subheader("Parámetros")
    st.radio("Hipótesis alternativa", pz.COLAS, key="z_cola", horizontal=True, on_change=_al_cambiar_cola,
             format_func=lambda c: "Hₐ: μ > μ₀" if c == "superior" else "Hₐ: μ < μ₀")
    a1, a2 = st.columns(2)
    a1.number_input("μ₀ (bajo H₀)", step=0.1, format="%.3f", key="z_mu0")
    a2.number_input("μ₁ (alternativa específica)", step=0.1, format="%.3f", key="z_mu1")
    a3, a4 = st.columns(2)
    a3.number_input("σ (conocida)", min_value=0.001, step=0.1, format="%.3f", key="z_sigma")
    a4.number_input("n", min_value=1, max_value=5000, step=1, key="z_n")
    st.number_input("α (nivel de significancia)", min_value=0.001, max_value=0.5, step=0.005, format="%.3f",
                    key="z_alfa")
    st.radio("Frontera de rechazo", MODOS, key="z_modo")

ok, msg = estado.z_valida()
if not ok:
    with col_g:
        st.error(msg)
    st.stop()

cfg = estado.config_z()
k_alfa = pz.frontera(cfg)
ee = cfg.ee
if ss.z_modo == MODOS[1]:
    lo = float(min(cfg.mu0, cfg.mu1) - 3 * ee)
    hi = float(max(cfg.mu0, cfg.mu1) + 3 * ee)
    if "z_k" not in ss or not lo <= ss.z_k <= hi:
        ss.z_k = float(np.clip(k_alfa, lo, hi))
    with col_c:
        st.slider("Frontera k", lo, hi, step=float(ee / 50), format="%.4f", key="z_k")
    k = float(ss.z_k)
else:
    k = k_alfa
r = pz.resumen(cfg, k)
signo_rr = ">" if cfg.cola == "superior" else "<"

with col_g:
    ui.cifras([
        ("α = P(error tipo I)", ui.fmt(r["alfa"]), f"P(Ȳ {signo_rr} {k:.3f} | μ = {cfg.mu0:g})", ALFA),
        ("β(μ₁) = P(error tipo II)", ui.fmt(r["beta"]), f"P(Ȳ no {signo_rr} {k:.3f} | μ = {cfg.mu1:g})", BETA),
        ("Potencia en μ₁", ui.fmt(r["potencia"]), "1 − β(μ₁)", POTENCIA),
        ("Frontera k", ui.fmt(k), f"EE = σ/√n = {ee:.4f}", NAVY),
    ])
    st.plotly_chart(gr.normales(cfg, k), width="stretch")

st.markdown(
    f"**Regla:** rechazar H₀ si ȳ {signo_rr} k, con $k = \\mu_0 {'+' if cfg.cola == 'superior' else '-'} "
    f"z_\\alpha \\, \\sigma/\\sqrt{{n}} = {cfg.mu0:g} {'+' if cfg.cola == 'superior' else '-'} "
    f"{r['z_alfa']:.4f} \\times {ee:.4f} = {k_alfa:.4f}$ cuando se fija α = {cfg.alfa:g}.")

st.header("¿Por qué no se pueden bajar los dos a la vez?")
c1, c2 = st.columns([1.15, 1], gap="large")
with c1:
    if cfg.cola == "superior":
        st.latex(r"\alpha(k) = P(\bar Y > k \mid \mu_0) = 1 - \Phi\!\left(\frac{k-\mu_0}{\sigma/\sqrt n}\right)")
        st.latex(r"\beta(k) = P(\bar Y \le k \mid \mu_1) = \Phi\!\left(\frac{k-\mu_1}{\sigma/\sqrt n}\right)")
        mov = "subir k (alejarla de μ₀ hacia μ₁)"
    else:
        st.latex(r"\alpha(k) = P(\bar Y < k \mid \mu_0) = \Phi\!\left(\frac{k-\mu_0}{\sigma/\sqrt n}\right)")
        st.latex(r"\beta(k) = P(\bar Y \ge k \mid \mu_1) = 1 - \Phi\!\left(\frac{k-\mu_1}{\sigma/\sqrt n}\right)")
        mov = "bajar k (alejarla de μ₀ hacia μ₁)"
    st.markdown(
        f"Φ es creciente. Hacer la regla **más estricta** es {mov}: la región de rechazo se encoge. "
        "Entonces queda menos área de la campana de H₀ dentro de la región (**α baja**) y, como la campana "
        "de μ₁ es la misma, queda más área suya fuera de la región (**β sube**). Las dos probabilidades "
        "dependen de la misma k y se mueven en sentido contrario.")
    st.markdown("Lo único que cambia esa relación, con σ y μ₁ fijos, es **n**: el error estándar σ/√n se "
                "achica, las campanas se separan y las dos áreas pueden bajar a la vez.")
with c2:
    st.plotly_chart(gr.alfa_beta_vs_k(cfg, k), width="stretch")

st.header("α, β y el tamaño de muestra (conexión con la Sección 10.4)")
c1, c2 = st.columns([1, 2], gap="large")
with c1:
    st.number_input("β deseado en μ₁", min_value=0.001, max_value=0.9, step=0.01, format="%.3f", key="z_beta_obj")
    n_req = pz.n_requerido(cfg.mu0, cfg.mu1, cfg.sigma, cfg.alfa, float(ss.z_beta_obj))
    st.latex(r"n = \frac{(z_\alpha + z_\beta)^2\,\sigma^2}{(\mu_1-\mu_0)^2}")
    st.metric("n requerido", n_req, delta=f"{n_req - cfg.n:+d} respecto al n actual", delta_color="off")
    st.caption(f"Con α = {cfg.alfa:g} y β = {ss.z_beta_obj:g} en μ₁ = {cfg.mu1:g}. Se redondea hacia arriba.")
with c2:
    st.plotly_chart(gr.beta_vs_n(cfg, n_req), width="stretch")

st.header("Conexión con la segunda aplicación")
st.markdown("«Del riesgo a la evidencia: potencia y tamaño muestral» puede importar esta misma configuración. "
            "El archivo incluye μ₀, μ₁, σ, n, α y el tipo de prueba (solo parámetros de la prueba Z: los de la "
            "binomial no se usan en fórmulas para medias).")
c1, c2 = st.columns(2, gap="large")
with c1:
    st.download_button("Descargar configuración JSON", pz.a_json(cfg), file_name="config_prueba_Z.json",
                       mime="application/json", type="primary", width="stretch")
    with st.expander("Ver el JSON"):
        st.code(pz.a_json(cfg), language="json")
with c2:
    st.file_uploader("Cargar una configuración JSON", type=["json"], key="z_json")
    st.button("Usar esta configuración", on_click=_cargar_json, disabled=ss.get("z_json") is None,
              width="stretch")
    if "z_json_msg" in ss:
        tipo, texto = ss.pop("z_json_msg")
        (st.success if tipo == "ok" else st.error)(texto)
