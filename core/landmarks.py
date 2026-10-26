"""
landmarks.py
------------
Extrae los puntos (landmarks) específicos de los ojos
a partir de los resultados de MediaPipe.

Este archivo NO sabe nada de MediaPipe directamente.
Solo recibe resultados ya procesados y saca los índices que le interesan.
Tampoco calcula EAR. Eso es tarea de ear.py.

FASE: Semana 1, Días 3-4 (Módulo de visión)
"""

from __future__ import annotations

from typing import Any


class LandmarksExtractor:
    """
    Sabe extraer los puntos de los ojos de los resultados de MediaPipe.

    Uso:
        extractor = LandmarksExtractor()
        izq = extractor.extraer_ojo_izquierdo(resultados)
        der = extractor.extraer_ojo_derecho(resultados)
    """

    def __init__(self):
        # Índices de los 6 puntos que forman cada ojo.
        # Constantes, nunca cambian durante la ejecución.
        self.left_eye_indices = [362, 385, 387, 263, 373, 380]
        self.right_eye_indices = [33, 160, 158, 133, 153, 144]

    def _extraer_puntos(self, resultados: Any, indices: list[int]) -> list:
        """Método privado que saca los puntos usando una lista de índices."""
        if not resultados.multi_face_landmarks:
            return []

        face_landmarks = resultados.multi_face_landmarks[0]
        return [face_landmarks.landmark[i] for i in indices]

    def extraer_ojo_izquierdo(self, resultados: Any) -> list:
        """Devuelve los 6 puntos del ojo izquierdo."""
        return self._extraer_puntos(resultados, self.left_eye_indices)

    def extraer_ojo_derecho(self, resultados: Any) -> list:
        """Devuelve los 6 puntos del ojo derecho."""
        return self._extraer_puntos(resultados, self.right_eye_indices)