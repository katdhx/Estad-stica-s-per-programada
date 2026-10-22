import numpy as np
import streamlit as st

from nucleo import binomial as bn
from nucleo import estado
from nucleo import pruebaz as pz
from nucleo import ui
from nucleo.ui import ALFA, BETA, NAVY, POTENCIA

ui.preparar()
ss = st.session_state
PRUEBAS = ("Prueba Z (Módulo 2)", "Binomial de Jones (Módulo 1)")
RECH, NO_RECH = "Rechazar H₀", "No rechazar H₀"
if "d_marcador" not in ss:
    ss.d_marcador = {"rondas": 0, "correctas": 0, "tipo I": 0, "tipo II": 0}


def _nuevo():
    rng = np.random.default_rng()
    h0 = bool(rng.random() < 0.5)
    if ss.d_prueba == PRUEBAS[0]:
        cfg = estado.config_z()
        mu = cfg.mu0 if h0 else cfg.mu1
        x = rng.normal(mu, cfg.sigma, cfg.n)
        ybar = float(x.mean())
        z = float(pz.estadistico(ybar, cfg))
        ss.d_exp = {"tipo": "z", "h0": h0, "verdadero": mu, "x": x, "ybar": ybar, "z": z,
                    "rechaza_regla": bool(pz.rechaza_z(z, cfg)), "cfg": cfg, "k": pz.frontera(cfg), "usuario": None}
    else:
        b = estado.binom()
        p = b["p0"] if h0 else b["p1"]
        y = int(rng.binomial(b["n"], p))
        ss.d_exp = {"tipo": "b", "h0": h0, "verdadero": p, "y": y, "b": b,
                    "rechaza_regla": bool(bn.en_region(y, b["c"], b["cola"])), "usuario": None}


def _decidir(eleccion: str):
    e = ss.d_exp
    e["usuario"] = eleccion
    rechaza = eleccion == RECH
    m = ss.d_marcador
    m["rondas"] += 1
    if e["h0"] and rechaza:
        m["tipo I"] += 1
    elif not e["h0"] and not rechaza:
        m["tipo II"] += 1
    else:
        m["correctas"] += 1


def _reiniciar():
    ss.d_marcador = {"rondas": 0, "correctas": 0, "tipo I": 0, "tipo II": 0}
    ss.pop("d_exp", None)


ui.encabezado(
    "Módulo 4 · Toma una decisión",
    "La aplicación lanza una moneda en secreto: la mitad de las veces H₀ es verdadera y la otra mitad lo es la "
    "alternativa específica. Genera una muestra y te muestra el estadístico. Tú decides.",
    "Sección 10.2: el error tipo I y el error tipo II se definen comparando la decisión con el estado verdadero, "
    "que en la práctica no se conoce.")

col_c, col_j = st.columns([1, 2.3], gap="large")
with col_c:
    st.radio("Prueba", PRUEBAS, key="d_prueba")
    ok, msg = estado.z_valida() if ss.d_prueba == PRUEBAS[0] else estado.binom_valida()
    if not ok:
        st.error(msg)
    st.button("Nuevo experimento", type="primary", on_click=_nuevo, disabled=not ok, width="stretch")
    m = ss.d_marcador
    st.subheader("Marcador del público")
    ui.cifras([("Rondas", str(m["rondas"]), "", NAVY), ("Correctas", str(m["correctas"]), "", POTENCIA)])
    ui.cifras([("Errores tipo I", str(m["tipo I"]), "", ALFA), ("Errores tipo II", str(m["tipo II"]), "", BETA)])
    st.button("Reiniciar marcador", on_click=_reiniciar, width="stretch")

e = ss.get("d_exp")
with col_j:
    if e is None or (e["tipo"] == "z") != (ss.d_prueba == PRUEBAS[0]):
        st.info("Pulsa **Nuevo experimento** para empezar.")
        st.stop()
    if e["tipo"] == "z":
        cfg = e["cfg"]
        st.markdown(f"**H₀: μ = {cfg.mu0:g}** contra **Hₐ: μ {'>' if cfg.cola == 'superior' else '<'} {cfg.mu0:g}**  "
                    f"· σ = {cfg.sigma:g} conocida · n = {cfg.n} · nivel α = {cfg.alfa:g}")
        ui.cifras([("Media muestral observada ȳ", ui.fmt(e["ybar"]), f"de {cfg.n} observaciones", NAVY),
                   ("Estadístico z = (ȳ − μ₀)/(σ/√n)", ui.fmt(e["z"], 3), "", NAVY)])
    else:
        b = e["b"]
        st.markdown(f"**H₀: p = {b['p0']:.2f}** contra **Hₐ: p {'<' if b['cola'] == 'inferior' else '>'} "
                    f"{b['p0']:.2f}** · n = {b['n']} votantes")
        ui.cifras([("Votantes a favor observados Y", str(e["y"]), f"de {b['n']}", NAVY),
                   ("Proporción observada", ui.fmt(e["y"] / b["n"], 3), f"bajo H₀ se esperaría {b['p0']:.2f}", NAVY)])

    if e["usuario"] is None:
        st.markdown("### ¿Qué decides?")
        d1, d2 = st.columns(2)
        d1.button(RECH, on_click=_decidir, args=(RECH,), width="stretch", type="primary")
        d2.button(NO_RECH, on_click=_decidir, args=(NO_RECH,), width="stretch")
        st.stop()

    rechaza_u = e["usuario"] == RECH
    if e["tipo"] == "z":
        cfg = e["cfg"]
        regla = (f"rechazar H₀ si z {'>' if cfg.cola == 'superior' else '<'} "
                 f"{'' if cfg.cola == 'superior' else '−'}{pz.z_cola(cfg.alfa):.3f} "
                 f"(equivalente: ȳ {'>' if cfg.cola == 'superior' else '<'} {e['k']:.4f})")
        verdad = f"μ = {e['verdadero']:g} → " + ("H₀ era verdadera" if e["h0"] else "la alternativa era verdadera")
    else:
        b = e["b"]
        regla = f"rechazar H₀ si y {'≤' if b['cola'] == 'inferior' else '≥'} {b['c']}"
        verdad = f"p = {e['verdadero']:.2f} → " + ("H₀ era verdadera" if e["h0"] else "la alternativa era verdadera")
    if e["h0"] and rechaza_u:
        veredicto, color = "Error tipo I: rechazaste H₀ y era verdadera.", ALFA
    elif not e["h0"] and not rechaza_u:
        veredicto, color = "Error tipo II: no rechazaste H₀ y era falsa.", BETA
    else:
        veredicto, color = "Decisión correcta.", POTENCIA
    st.markdown(f"### {ui.etiqueta(veredicto, color)}", unsafe_allow_html=True)
    st.markdown(f"- **Tu decisión:** {e['usuario']}\n"
                f"- **La regla de la prueba:** {regla} → **{RECH if e['rechaza_regla'] else NO_RECH}**\n"
                f"- **Estado verdadero usado para generar la muestra:** {verdad}")
    if e["rechaza_regla"] != rechaza_u:
        st.markdown("Tu decisión no coincide con la regla de nivel α. " + (
            "La regla también se habría equivocado aquí." if (e["h0"] == e["rechaza_regla"]) else
            "Aquí la regla sí acertaba."))
    elif (e["h0"] and e["rechaza_regla"]) or (not e["h0"] and not e["rechaza_regla"]):
        st.markdown("Seguiste la regla y aun así hubo error: es exactamente el riesgo que miden α y β. "
                    "Una buena regla no evita los errores, controla con qué frecuencia ocurren.")
    ui.caja("Conocemos la verdad <b>solo porque es una simulación</b>: la app eligió el parámetro antes de generar "
            "los datos. Con datos reales nunca sabremos si una decisión concreta fue un error; solo conocemos "
            "la probabilidad de equivocarnos que tiene la regla.", aviso=True)
    st.button("Otro experimento", on_click=_nuevo, type="primary")
