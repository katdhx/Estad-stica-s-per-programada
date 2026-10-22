"""Laboratorio de intervalos de confianza.

Paquete con el motor matemático y computacional de la aplicación. Toda la
matemática está fundamentada en Wackerly, Mendenhall y Scheaffer,
*Estadística matemática con aplicaciones*, 7.ª edición, capítulos 7 y 8.

Módulos
-------
poblaciones     Distribuciones poblacionales disponibles para muestrear.
intervalos      Fórmulas de los intervalos de confianza (funciones puras, vectorizadas).
procedimientos  Catálogo de procedimientos con su ficha matemática completa.
motor           Motor de Monte Carlo por lotes (memoria acotada, reproducible).
teoria          Resultados teóricos (amplitudes esperadas, coberturas exactas).
graficos        Constructores de figuras Plotly con la identidad visual del laboratorio.
ejemplos_libro  Ejemplos numéricos del libro usados para validar el código.
"""

__version__ = "1.0.0"
