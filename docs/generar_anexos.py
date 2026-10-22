"""Genera los anexos del documento matemático a partir del código.

Así, las fichas de los procedimientos y la tabla de correspondencia del
documento son exactamente las mismas que muestra la aplicación.

Uso:  python docs/generar_anexos.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from lab.correspondencia import FILAS, PROCEDIMIENTOS_LIBRO  # noqa: E402
from lab.procedimientos import PROCEDIMIENTOS  # noqa: E402


def fichas() -> str:
    partes = ["# Anexo A. Fichas de los procedimientos\n",
              "Generado automáticamente desde `lab/procedimientos.py`; es el mismo texto que muestra la aplicación.\n"]
    for p in PROCEDIMIENTOS.values():
        partes.append(f"\n## {p.nombre}\n")
        partes.append(f"**1. Parámetro.** ${p.parametro_latex}$: {p.parametro}\n")
        partes.append(f"**2. Estimador.**\n\n$$\n{p.estimador}\n$$\n")
        partes.append(f"**3. Distribución muestral.**\n\n$$\n{p.distribucion_muestral}\n$$\n")
        partes.append(f"**4. Estadístico pivotal.**\n\n$$\n{p.pivote}\n$$\n")
        partes.append(f"**5. Fórmula del intervalo.**\n\n$$\n{p.formula}\n$$\n\nLímites unilaterales:\n\n$$\n{p.formula_unilateral}\n$$\n")
        partes.append("**6. Supuestos.**\n\n" + "\n".join(f"- {s}" for s in p.supuestos) + "\n")
        partes.append("**7. Justificación matemática.**\n" + p.justificacion + "\n")
        partes.append(f"**8. Interpretación.** {p.interpretacion}\n")
        partes.append("**9. Referencias.** " + "; ".join(p.referencias) + ".\n")
        partes.append(f"**Tipo de resultado.** {p.exactitud}.\n")
    return "\n".join(partes)


def correspondencia() -> str:
    lin = ["# Anexo B. Tabla de correspondencia con el libro\n",
           "Generado desde `lab/correspondencia.py`. Las páginas son las del libro impreso (en el PDF hay que sumar 24).\n",
           "## Módulos de la aplicación\n",
           "| Módulo | Archivo | Resultado del libro | Sección | Página | Qué se comprueba |",
           "|---|---|---|---|---|---|"]
    lin += [f"| {a} | `{b}` | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in FILAS]
    lin += ["", "## Procedimientos de intervalos de confianza\n",
            "| Procedimiento | Sección | Ejemplos | Se apoya en | Tipo |", "|---|---|---|---|---|"]
    lin += [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in PROCEDIMIENTOS_LIBRO]
    return "\n".join(lin) + "\n"


if __name__ == "__main__":
    (RAIZ / "docs" / "anexo_A_fichas.md").write_text(fichas(), encoding="utf-8")
    (RAIZ / "docs" / "anexo_B_correspondencia.md").write_text(correspondencia(), encoding="utf-8")
    print("Anexos generados en docs/.")
