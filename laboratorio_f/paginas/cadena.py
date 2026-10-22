import numpy as np
import pandas as pd
import streamlit as st

from nucleo import fdist, graficos as gr
from nucleo import motor, teoria, ui
from nucleo.poblaciones import Poblacion

P = "cad"
ui.preparar()
ui.encabezado(
    "2. Dónde se rompe la cadena",
    "La F del libro sale de una cadena de cuatro resultados. Aquí se revisa cada eslabón por separado, con las mismas "
    "muestras, para ver exactamente en cuál falla cuando las poblaciones no son normales.",
    "Ejemplo 8.1 (p. 398), Teorema 7.3 (p. 357), Definición 7.3 (p. 362).",
)

st.sidebar.header("Escenario")
f1 = ui.selector_forma(f"{P}_1", "Forma de la población 1", "t", valor_defecto=5.0)
f2 = ui.selector_forma(f"{P}_2", "Forma de la población 2", "t", valor_defecto=5.0)
c1, c2 = st.sidebar.columns(2)
n1 = int(c1.number_input("n₁", 2, motor.N_MAX, 15, key=f"{P}_n1"))
n2 = int(c2.number_input("n₂", 2, motor.N_MAX, 15, key=f"{P}_n2"))
B = int(st.sidebar.number_input("Pares de muestras B", 1000, motor.B_MAX, 30000, 1000, key=f"{P}_B"))
esc = motor.Escenario(Poblacion(f1), Poblacion(f2), n1, n2, B, 2026)
ui.costo(esc)
bloq = ui.mostrar_errores(esc.validar())
if ui.boton(P, deshabilitado=bloq):
    b, av = ui.barra()
    r = ui.simular(esc, av)
    b.empty()
    ui.guardar(P, esc, r)
res, viejo = ui.recuperar(P, esc)
if res is None:
    st.info("Pulsa «Ejecutar simulación». Por defecto, las dos poblaciones son t con 5 grados de libertad: simétricas, "
            "pero con colas pesadas.")
    st.stop()
if viejo:
    ui.aviso_desactualizado()
E = res.escenario
g1, g2 = E.gl
normal1, normal2 = E.pob1.forma.es_normal, E.pob2.forma.es_normal
k1, k2 = E.pob1.forma.curtosis(), E.pob2.forma.curtosis()

ui.cadena(E.pob1.forma, E.pob2.forma, motor.cobertura(res, 0.05).estimada)

# --------------------------------------------------------------- eslabón 1
st.header("Eslabón 1: S² apunta al valor correcto")
r1, r2 = res.s2_1 / E.pob1.varianza, res.s2_2 / E.pob2.varianza
c = st.columns(2)
c[0].metric("Promedio de S₁²/σ₁² en las réplicas", f"{r1.mean():.4f}", help="Debe ser 1 (Ejemplo 8.1).")
c[1].metric("Promedio de S₂²/σ₂² en las réplicas", f"{r2.mean():.4f}", help="Debe ser 1 (Ejemplo 8.1).")
ui.veredicto("<b>Este eslabón nunca se rompe.</b> E(S²) = σ² para cualquier población con varianza finita (Ejemplo 8.1). "
             "Los dos promedios dan ≈ 1, sea cual sea la forma. El problema no está en el centro de S².", True)

# --------------------------------------------------------------- eslabón 2
st.header("Eslabón 2: ¿cuánto varía S²?")
st.markdown("El Teorema 7.3 implica que V(S²/σ²) = 2/(n − 1), porque V(χ²ₙ₋₁) = 2(n − 1). "
            "Para cualquier forma, en cambio, vale V(S²/σ²) = 2/(n − 1) + κ/n (complementario).")
tabla = pd.DataFrame({
    "": ["Población 1", "Población 2"],
    "Forma": [E.pob1.forma.nombre_corto(), E.pob2.forma.nombre_corto()],
    "Curtosis κ": [k1, k2],
    "V(S²/σ²) simulada": [r1.var(ddof=1), r2.var(ddof=1)],
    "Lo que supone la χ²: 2/(n−1)": [2 / (E.n1 - 1), 2 / (E.n2 - 1)],
    "Fórmula general: 2/(n−1) + κ/n": [teoria.varianza_s2(1, E.n1, k1), teoria.varianza_s2(1, E.n2, k2)],
})
tabla["Razón simulada / χ²"] = tabla["V(S²/σ²) simulada"] / tabla["Lo que supone la χ²: 2/(n−1)"]
st.dataframe(tabla.style.format({c: "{:.4f}" for c in tabla.columns if c not in ("", "Forma")}).format(
    {"Curtosis κ": lambda v: "∞" if not np.isfinite(v) else f"{v:.2f}"}), hide_index=True, use_container_width=True)
if normal1 and normal2:
    ui.veredicto("<b>Se cumple.</b> La varianza simulada coincide con 2/(n − 1).", True)
else:
    peor = max(tabla["Razón simulada / χ²"])
    ui.veredicto(f"<b>Aquí se rompe la cadena.</b> S² varía hasta {peor:.2f} veces lo que supone la χ². La fórmula general "
                 "con la curtosis sí acierta. Con colas pesadas, S² a veces sale muy grande y a veces muy pequeña, más de lo "
                 "que la teoría normal permite." if peor > 1 else
                 "<b>Aquí se rompe la cadena, al revés.</b> S² varía menos de lo que supone la χ² (colas livianas).", False)

# --------------------------------------------------------------- eslabón 3
st.header("Eslabón 3: ¿es W una χ²?")
cA, cB = st.columns(2)
with cA:
    ui.figura(gr.histograma_chi2(res.W1, g1, f"W₁ = (n₁−1)S₁²/σ₁² frente a χ²({g1})", normal1, etiqueta_x="W₁"),
              "cadena_w1", f"{P}_w1")
with cB:
    ui.figura(gr.histograma_chi2(res.W2, g2, f"W₂ = (n₂−1)S₂²/σ₂² frente a χ²({g2})", normal2, etiqueta_x="W₂"),
              "cadena_w2", f"{P}_w2")
ui.nota("Las dos curvas tienen la misma media (n − 1), por el eslabón 1. Lo que cambia es el ancho: con colas pesadas el "
        "histograma tiene más valores pegados a 0 y una cola derecha más larga que la χ².")

# --------------------------------------------------------------- eslabón 4
st.header("Eslabón 4: el cociente F*")
st.markdown("La Definición 7.3 necesita dos cosas: que W₁ y W₂ sean χ² y que sean independientes. La independencia **se "
            "cumple siempre**, porque las muestras son independientes. Lo que falla es lo primero, y la F lo hereda.")
a, b = fdist.intervalo_central(0.05, E.n1, E.n2)
fig = gr.histograma_f(res.F_pivote, g1, g2, f"F* frente a F({g1}, {g2})", region=(a, b),
                      exacta=normal1 and normal2, x="F*", etiqueta_region="2.5 % de cada cola según la F")
ui.figura(fig, "cadena_f", f"{P}_f")
cob = motor.cobertura(res, 0.05)
ui.veredicto(f"Fuera del 95 % central de la F cae el <b>{100 * (1 - cob.estimada):.1f} %</b> de los valores de F* "
             f"(la F promete 5 %). Error estándar de la simulación: {100 * cob.error_estandar:.2f} puntos.",
             cob.compatible())
