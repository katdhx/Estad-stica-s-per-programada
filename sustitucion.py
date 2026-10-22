"""Escritura en LaTeX de un intervalo con los números ya sustituidos.

Se usa en la inspección de un intervalo individual (Experimento 1) y en la
calculadora. El objetivo es que en la sustentación se vea la cuenta completa,
no solo el resultado.
"""

from __future__ import annotations

import numpy as np

from . import intervalos as ic


def _f(x: float, d: int = 4) -> str:
    if not np.isfinite(x):
        return r"\infty" if x > 0 else r"-\infty"
    return f"{x:.{d}f}"


def lineas(clave: str, e: dict, alfa: float, lado: str = "bilateral", sigma: float | None = None) -> list[str]:
    """Devuelve una lista de expresiones LaTeX, una por paso."""
    a2 = alfa / 2
    out: list[str] = []
    nivel = f"{100 * (1 - alfa):g}\\%"
    if clave in ("media_z_sigma", "media_z_s", "media_t"):
        n = int(e["n"])
        ybar = float(e["media"])
        if clave == "media_z_sigma":
            dis, simb = sigma, r"\sigma"
        else:
            dis, simb = float(np.sqrt(e["var"])), "s"
        ee = dis / np.sqrt(n)
        if clave == "media_t":
            c2, c1 = ic.t_critico(a2, n - 1), ic.t_critico(alfa, n - 1)
            nom2, nom1 = f"t_{{{a2:g},\\,{n - 1}}}", f"t_{{{alfa:g},\\,{n - 1}}}"
        else:
            c2, c1 = ic.z_critico(a2), ic.z_critico(alfa)
            nom2, nom1 = f"z_{{{a2:g}}}", f"z_{{{alfa:g}}}"
        out.append(rf"n = {n},\quad \bar y = {_f(ybar)},\quad {simb} = {_f(dis)},\quad \frac{{{simb}}}{{\sqrt n}} = {_f(ee)}")
        if lado == "bilateral":
            out.append(rf"{nom2} = {_f(c2)}\quad(\text{{área }} {a2:g} \text{{ en cada cola}})")
            out.append(rf"\bar y \pm {nom2}\frac{{{simb}}}{{\sqrt n}} = {_f(ybar)} \pm {_f(c2)}\times{_f(ee)} = {_f(ybar)} \pm {_f(c2 * ee)}")
            out.append(rf"\text{{IC del }}{nivel}:\ [{_f(ybar - c2 * ee)},\ {_f(ybar + c2 * ee)}]")
        elif lado == "inferior":
            out.append(rf"{nom1} = {_f(c1)},\qquad \bar y - {nom1}\frac{{{simb}}}{{\sqrt n}} = {_f(ybar - c1 * ee)}")
            out.append(rf"\text{{Límite inferior del }}{nivel}:\ [{_f(ybar - c1 * ee)},\ \infty)")
        else:
            out.append(rf"{nom1} = {_f(c1)},\qquad \bar y + {nom1}\frac{{{simb}}}{{\sqrt n}} = {_f(ybar + c1 * ee)}")
            out.append(rf"\text{{Límite superior del }}{nivel}:\ (-\infty,\ {_f(ybar + c1 * ee)}]")
        return out

    if clave == "varianza_chi2":
        n = int(e["n"])
        s2 = float(e["var"])
        sc = (n - 1) * s2
        out.append(rf"n = {n},\quad s^2 = {_f(s2)},\quad (n-1)s^2 = {_f(sc)},\quad \text{{gl}} = {n - 1}")
        if lado == "bilateral":
            ca, cb = ic.chi2_critico(a2, n - 1), ic.chi2_critico(1 - a2, n - 1)
            out.append(rf"\chi^2_{{{a2:g}}} = {_f(ca)},\qquad \chi^2_{{{1 - a2:g}}} = {_f(cb)}")
            out.append(rf"\left[\frac{{{_f(sc)}}}{{{_f(ca)}}},\ \frac{{{_f(sc)}}}{{{_f(cb)}}}\right] = [{_f(sc / ca)},\ {_f(sc / cb)}]")
        elif lado == "inferior":
            ca = ic.chi2_critico(alfa, n - 1)
            out.append(rf"\chi^2_{{{alfa:g}}} = {_f(ca)},\qquad \frac{{(n-1)s^2}}{{\chi^2_{{{alfa:g}}}}} = {_f(sc / ca)}")
        else:
            cb = ic.chi2_critico(1 - alfa, n - 1)
            out.append(rf"\chi^2_{{{1 - alfa:g}}} = {_f(cb)},\qquad \frac{{(n-1)s^2}}{{\chi^2_{{{1 - alfa:g}}}}} = {_f(sc / cb)}")
        return out

    if clave == "exponencial_chi2":
        n = int(e["n"])
        s = float(e["suma"])
        out.append(rf"n = {n},\quad \textstyle\sum y_i = {_f(s)},\quad 2\sum y_i = {_f(2 * s)},\quad \text{{gl}} = 2n = {2 * n}")
        if lado == "bilateral":
            ca, cb = ic.chi2_critico(a2, 2 * n), ic.chi2_critico(1 - a2, 2 * n)
            out.append(rf"\chi^2_{{{a2:g}}} = {_f(ca)},\qquad \chi^2_{{{1 - a2:g}}} = {_f(cb)}")
            out.append(rf"\left[\frac{{{_f(2 * s)}}}{{{_f(ca)}}},\ \frac{{{_f(2 * s)}}}{{{_f(cb)}}}\right] = [{_f(2 * s / ca)},\ {_f(2 * s / cb)}]")
        else:
            L, U = ic.exponencial_chi2(s, n, alfa, lado)
            out.append(rf"[{_f(float(L))},\ {_f(float(U))}]")
        return out

    if clave == "proporcion_wald":
        n = int(e["n"])
        y = float(e["exitos"])
        ph = y / n
        ee = np.sqrt(ph * (1 - ph) / n)
        z = ic.z_critico(a2) if lado == "bilateral" else ic.z_critico(alfa)
        out.append(rf"y = {y:g},\ n = {n},\quad \hat p = {_f(ph)},\quad \sqrt{{\hat p\hat q/n}} = {_f(ee)}")
        if lado == "bilateral":
            out.append(rf"\hat p \pm z_{{{a2:g}}}\sqrt{{\hat p\hat q/n}} = {_f(ph)} \pm {_f(z)}\times{_f(ee)} = [{_f(ph - z * ee)},\ {_f(ph + z * ee)}]")
            if ph in (0.0, 1.0):
                out.append(r"\hat p\in\{0,1\}\Rightarrow \sqrt{\hat p\hat q/n}=0:\ \text{el intervalo se reduce a un punto.}")
        else:
            L, U = ic.proporcion_wald(ph, n, alfa, lado)
            out.append(rf"z_{{{alfa:g}}} = {_f(z)},\qquad [{_f(float(L))},\ {_f(float(U))}]")
        return out

    if clave in ("dif_medias_z", "dif_medias_t"):
        n1, n2 = int(e["n1"]), int(e["n2"])
        m1, m2, v1, v2 = (float(e[k]) for k in ("media1", "media2", "var1", "var2"))
        d = m1 - m2
        out.append(rf"\bar y_1 = {_f(m1)},\ s_1^2 = {_f(v1)},\ n_1 = {n1};\qquad \bar y_2 = {_f(m2)},\ s_2^2 = {_f(v2)},\ n_2 = {n2}")
        if clave == "dif_medias_z":
            ee = np.sqrt(v1 / n1 + v2 / n2)
            c = ic.z_critico(a2)
            out.append(rf"\sqrt{{s_1^2/n_1 + s_2^2/n_2}} = {_f(ee)},\qquad z_{{{a2:g}}} = {_f(c)}")
        else:
            sp2 = float(ic.varianza_agrupada(v1, v2, n1, n2))
            ee = np.sqrt(sp2) * np.sqrt(1 / n1 + 1 / n2)
            c = ic.t_critico(a2, n1 + n2 - 2)
            out.append(rf"s_p^2 = \frac{{{n1 - 1}({_f(v1)}) + {n2 - 1}({_f(v2)})}}{{{n1 + n2 - 2}}} = {_f(sp2)},\quad s_p = {_f(np.sqrt(sp2))}")
            out.append(rf"t_{{{a2:g},\,{n1 + n2 - 2}}} = {_f(c)},\qquad s_p\sqrt{{1/n_1+1/n_2}} = {_f(ee)}")
        out.append(rf"({_f(m1)} - {_f(m2)}) \pm {_f(c)}\times{_f(ee)} = {_f(d)} \pm {_f(c * ee)} = [{_f(d - c * ee)},\ {_f(d + c * ee)}]")
        return out

    if clave == "dif_proporciones":
        n1, n2 = int(e["n1"]), int(e["n2"])
        p1, p2 = float(e["exitos1"]) / n1, float(e["exitos2"]) / n2
        ee = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
        c = ic.z_critico(a2)
        out.append(rf"\hat p_1 = {_f(p1)},\quad \hat p_2 = {_f(p2)},\quad \sqrt{{\tfrac{{\hat p_1\hat q_1}}{{n_1}}+\tfrac{{\hat p_2\hat q_2}}{{n_2}}}} = {_f(ee)},\quad z_{{{a2:g}}} = {_f(c)}")
        out.append(rf"{_f(p1 - p2)} \pm {_f(c * ee)} = [{_f(p1 - p2 - c * ee)},\ {_f(p1 - p2 + c * ee)}]")
        return out

    if clave == "razon_varianzas_f":
        n1, n2 = int(e["n1"]), int(e["n2"])
        v1, v2 = float(e["var1"]), float(e["var2"])
        r = v2 / v1
        fa, fb = ic.f_critico(a2, n1 - 1, n2 - 1), ic.f_critico(1 - a2, n1 - 1, n2 - 1)
        out.append(rf"s_1^2 = {_f(v1)},\ s_2^2 = {_f(v2)},\quad s_2^2/s_1^2 = {_f(r)},\quad \text{{gl}} = ({n1 - 1},\ {n2 - 1})")
        out.append(rf"F_{{{a2:g}}} = {_f(fa)},\qquad F_{{{1 - a2:g}}} = {_f(fb)}")
        out.append(rf"[{_f(r)}\times{_f(fb)},\ {_f(r)}\times{_f(fa)}] = [{_f(r * fb)},\ {_f(r * fa)}]")
        return out
    return out
