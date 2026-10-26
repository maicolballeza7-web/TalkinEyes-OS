"""
ear.py
------
Calcula el Eye Aspect Ratio (EAR): un número que dice qué tan abierto
está un ojo.

EAR alto → ojo abierto.
EAR bajo → ojo cerrado.

Este archivo NO usa MediaPipe. NO usa OpenCV. Solo matemáticas.
Recibe puntos y devuelve un número. Nada más.

"""
from __future__ import annotations

from typing import Any

import numpy as np


def calcular_ear(puntos_ojo: list, ancho_imagen: int, alto_imagen: int) -> float | None:
    """
    Calcula el EAR de UN ojo.

    Parámetros:
      - puntos_ojo: lista de 6 landmarks (de MediaPipe) del ojo.
      - ancho_imagen, alto_imagen: dimensiones del frame, para
        convertir coordenadas normalizadas (0.0 a 1.0) a píxeles.

    Devuelve:
      - el EAR (número flotante), o
      - None si la detección no fue confiable (ojo con el cálculo).
    """

    # MediaPipe devuelve los puntos en coordenadas "normalizadas":
    #   x=0.0 → borde izquierdo, x=1.0 → borde derecho
    #   y=0.0 → borde superior, y=1.0 → borde inferior
    # Para calcular distancias reales necesitamos multiplicar por
    # el ancho y alto en píxeles.
    #
    # Esto es exactamente lo que hacía tu V1 con:
    #   coordenadas = [(p.x * image_w, p.y * image_h) for p in eye_points]
    coordenadas = [
        (p.x * ancho_imagen, p.y * alto_imagen)
        for p in puntos_ojo
    ]
      # Si no hay exactamente 6 puntos, no podemos calcular el EAR.
    if len(coordenadas) != 6:
        return None

    # Los 6 puntos forman esta figura:
    #
    #     p2 ----- p3
    #        \   /
    #         p1        ← (esquina izquierda)
    #        /   \
    #     p6 ----- p5
    #         p4        ← (esquina derecha)
    #
    # (En realidad p1 y p4 son las esquinas horizontales,
    #  y p2-p6 / p3-p5 son las verticales.)
    p1, p2, p3, p4, p5, p6 = coordenadas

    # Distancia vertical 1: entre p2 y p6.
    vertical_1 = np.linalg.norm(np.array(p2) - np.array(p6))

    # Distancia vertical 2: entre p3 y p5.
    vertical_2 = np.linalg.norm(np.array(p3) - np.array(p5))

    # Distancia horizontal: entre p1 y p4.
    horizontal = np.linalg.norm(np.array(p1) - np.array(p4))

    # Protección: si la distancia horizontal es casi cero,
    # el cálculo se vuelve inestable (dividir por cero).
    # Preferimos descartar ese frame antes que dar un número basura.
    if horizontal < 1e-3:
        return None

    # La fórmula del EAR: promedio de las dos verticales,
    # dividido por la horizontal.
    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear


def calcular_ear_promedio(
    puntos_ojo_izq: list,
    puntos_ojo_der: list,
    ancho_imagen: int,
    alto_imagen: int,
) -> float | None:
    """
    Calcula el EAR promedio de los dos ojos.

    Es más estable que mirar un solo ojo, porque si uno de los
    dos falla (por oclusión, brillo, etc.), el otro compensa.

    Devuelve None si alguno de los dos ojos no se pudo calcular.
    """

    ear_izq = calcular_ear(puntos_ojo_izq, ancho_imagen, alto_imagen)
    ear_der = calcular_ear(puntos_ojo_der, ancho_imagen, alto_imagen)

    # Si alguno de los dos falló, no podemos promediar.
    if ear_izq is None or ear_der is None:
        return None

    return (ear_izq + ear_der) / 2.0
