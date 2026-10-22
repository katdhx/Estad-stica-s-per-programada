import re

import numpy as np
import pandas as pd
import streamlit as st

from lab import intervalos as ic
from lab import sustitucion, ui
from lab.ejemplos_libro import EJEMPLOS, estadisticos_desde
from lab.procedimientos import PROCEDIMIENTOS

P = "calc"
ui.preparar()
ui.encabezado(
    "Calculadora y ejemplos del libro",
    "Calcula un intervalo con datos reales mostrando cada paso, o reproduce los ejemplos resueltos del capítulo 8 "
    "y compara con el resultado impreso.",
    "Ejemplos 8.4, 8.7, 8.8, 8.11, 8.12 y 8.13; valores críticos de las Tablas 4 a 7 del Apéndice 3 citados en el capítulo 7.",
)


def leer_numeros(texto: str) -> np.ndarray:
    partes = [p for p in re.split(r"[\s;,]+", texto.strip()) if p]
    try:
        return np.array([float(p) for p in partes])
    except ValueError as e:
        raise ValueError("Escribe solo números separados por espacios, comas, punto y coma o saltos de línea. "
                         "Usa punto como separador decimal.") from e


t_ej, t_propios, t_tablas = st.tabs(["Ejemplos del libro", "Mis datos", "Valores críticos frente a las tablas"])

with t_ej:
    clave_ej = st.selectbox("Ejemplo", list(EJEMPLOS), format_func=lambda k: EJEMPLOS[k].titulo, key=f"{P}_ej")
    ej = EJEMPLOS[clave_ej]
    proc = PROCEDIMIENTOS[ej.procedimiento]
    st.markdown(f"**Enunciado (p. {ej.pagina}).** {ej.enunciado}")
    st.markdown(f"**Procedimiento:** {proc.nombre}. **Confianza:** {ej.confianza:.0%}.")
    if "y" in ej.datos:
        st.markdown("**Datos:** " + ", ".join(f"{v:g}" for v in ej.datos["y"]))
    if "y1" in ej.datos:
        st.markdown("**Muestra 1:** " + ", ".join(f"{v:g}" for v in ej.datos["y1"]))
        st.markdown("**Muestra 2:** " + ", ".join(f"{v:g}" for v in ej.datos["y2"]))
    e = estadisticos_desde(ej.procedimiento, ej.datos)
    alfa = 1 - ej.confianza
    for linea in sustitucion.lineas(ej.procedimiento, e, alfa):
        st.latex(linea)
    _, L, U = proc.calcular(e, alfa, "bilateral", None, None)
    L, U = float(L), float(U)
    c = st.columns(3)
    c[0].metric("Resultado de la app", f"[{L:.4f}, {U:.4f}]")
    c[1].metric("Resultado impreso en el libro", f"[{ej.esperado[0]:.4f}, {ej.esperado[1]:.4f}]")
    dif = max(abs(L - ej.esperado[0]), abs(U - ej.esperado[1]))
    c[2].metric("Diferencia máxima", f"{dif:.4f}")
    ui.veredicto(("<b>Coincide</b> con el libro dentro del redondeo de sus tablas. " if dif <= ej.tolerancia else
                  "<b>Hay una diferencia mayor a la esperada.</b> ") + ej.nota)

with t_propios:
    clave = st.selectbox("Procedimiento", list(PROCEDIMIENTOS), format_func=lambda k: PROCEDIMIENTOS[k].nombre,
                         key=f"{P}_proc")
    proc = PROCEDIMIENTOS[clave]
    c1, c2 = st.columns(2)
    conf = c1.number_input("Nivel de confianza (%)", 50.0, 99.9, 95.0, 0.5, key=f"{P}_conf")
    lado = c2.radio("Tipo de intervalo", list(ui.ETIQUETA_LADO), format_func=ui.ETIQUETA_LADO.get, horizontal=True,
                    key=f"{P}_lado")
    alfa = 1 - conf / 100
    try:
        sigma = None
        if clave in ("media_t", "media_z_s", "media_z_sigma", "varianza_chi2", "exponencial_chi2"):
            modo = st.radio("Entrada", ["Datos", "Resumen (n, ȳ, s²)"], horizontal=True, key=f"{P}_modo")
            if modo == "Datos":
                y = leer_numeros(st.text_area("Observaciones", "3005 2925 2935 2965 2995 3005 2937 2905", key=f"{P}_y"))
                e = estadisticos_desde(clave, {"y": y})
            else:
                cc = st.columns(3)
                n = int(cc[0].number_input("n", 1, 10**7, 64, key=f"{P}_n"))
                m = cc[1].number_input("ȳ", value=33.0, key=f"{P}_m", format="%.6f")
                v = cc[2].number_input("s²", 0.0, value=256.0, key=f"{P}_v", format="%.6f")
                e = {"n": n, "media": m, "var": v, "suma": m * n}
            if clave == "media_z_sigma":
                sigma = st.number_input("σ conocida", 0.000001, value=1.0, key=f"{P}_sigma", format="%.6f")
        elif clave in ("dif_medias_t", "dif_medias_z", "razon_varianzas_f"):
            a = leer_numeros(st.text_area("Muestra 1", "32 37 35 28 41 44 35 31 34", key=f"{P}_y1"))
            b = leer_numeros(st.text_area("Muestra 2", "35 31 29 25 34 40 27 32 31", key=f"{P}_y2"))
            e = estadisticos_desde(clave, {"y1": a, "y2": b})
        elif clave == "proporcion_wald":
            cc = st.columns(2)
            n = int(cc[0].number_input("n", 1, 10**9, 1000, key=f"{P}_pn"))
            y_ = int(cc[1].number_input("éxitos y", 0, n, min(560, n), key=f"{P}_py"))
            e = {"n": n, "exitos": y_}
        else:
            cc = st.columns(4)
            n1 = int(cc[0].number_input("n₁", 1, 10**9, 50, key=f"{P}_n1"))
            y1 = int(cc[1].number_input("éxitos₁", 0, n1, min(12, n1), key=f"{P}_y1p"))
            n2 = int(cc[2].number_input("n₂", 1, 10**9, 60, key=f"{P}_n2"))
            y2 = int(cc[3].number_input("éxitos₂", 0, n2, min(12, n2), key=f"{P}_y2p"))
            e = {"n1": n1, "exitos1": y1, "n2": n2, "exitos2": y2}
        if clave == "exponencial_chi2" and e["suma"] < 0:
            raise ValueError("Una exponencial no toma valores negativos.")
        if clave == "media_z_sigma":
            L, U = ic.media_z_sigma(e["media"], sigma, int(e["n"]), alfa, lado)
        else:
            _, L, U = proc.calcular(e, alfa, lado, None, None)
        for linea in sustitucion.lineas(clave, e, alfa, lado, sigma):
            st.latex(linea)
        ui.veredicto(f"<b>Intervalo del {conf:g} %:</b> [{ui.fmt(float(L))}, {ui.fmt(float(U))}]. "
                     f"Supuestos: {' '.join(proc.supuestos)}")
    except (ValueError, KeyError) as err:
        st.error(str(err))

with t_tablas:
    st.markdown("Valores que el capítulo 7 lee en las tablas del Apéndice 3, comparados con los que calcula SciPy. "
                "El subíndice es el área de la cola superior, como en el libro.")
    filas = [
        ("z.05", "Tabla 4; Ejemplo 8.7", 1.645, ic.z_critico(.05)),
        ("z.025", "Tabla 4; Ejemplo 7.3", 1.96, ic.z_critico(.025)),
        ("z.01", "Tabla 4; Ejemplo 8.8", 2.33, ic.z_critico(.01)),
        ("t.100 con 21 gl", "Tabla 5; p. 360", 1.323, ic.t_critico(.10, 21)),
        ("t.05 con 5 gl", "Tabla 5; Ejemplo 7.6", 2.015, ic.t_critico(.05, 5)),
        ("t.025 con 7 gl", "Tabla 5; Ejemplo 8.11", 2.365, ic.t_critico(.025, 7)),
        ("t.025 con 16 gl", "Tabla 5; Ejemplo 8.12", 2.120, ic.t_critico(.025, 16)),
        ("χ².90 con 10 gl", "Tabla 6; p. 356", 4.86518, ic.chi2_critico(.90, 10)),
        ("χ².05 con 6 gl", "Tabla 6; Ejemplo 7.4", 12.5916, ic.chi2_critico(.05, 6)),
        ("χ².05 con 9 gl", "Tabla 6; Ejemplo 7.5", 16.919, ic.chi2_critico(.05, 9)),
        ("χ².95 con 9 gl", "Tabla 6; Ejemplo 7.5", 3.325, ic.chi2_critico(.95, 9)),
        ("χ².05 con 2 gl", "Tabla 6; Ejemplo 8.13", 5.991, ic.chi2_critico(.05, 2)),
        ("χ².95 con 2 gl", "Tabla 6; Ejemplo 8.13", 0.103, ic.chi2_critico(.95, 2)),
        ("F.05 con (5, 9) gl", "Tabla 7; Ejemplo 7.7", 3.48, ic.f_critico(.05, 5, 9)),
        ("F.010 con (5, 7) gl", "Tabla 7; p. 362", 7.46, ic.f_critico(.01, 5, 7)),
    ]
    df = pd.DataFrame(filas, columns=["Valor", "Fuente en el libro", "Libro", "SciPy"])
    df["Diferencia"] = df["SciPy"] - df["Libro"]
    st.dataframe(df.style.format({"Libro": "{:.5f}", "SciPy": "{:.5f}", "Diferencia": "{:+.5f}"}), hide_index=True,
                 use_container_width=True)
    ui.nota("Todas las diferencias son de redondeo: las tablas imprimen tres o cuatro cifras.")
