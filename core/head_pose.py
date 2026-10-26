"""Estimación de la orientación de la cabeza usando landmarks de MediaPipe."""

from __future__ import annotations

from typing import Any

import cv2
import numpy as np


class HeadPoseEstimator:
    """Estima si una cara está orientada de frente a la cámara."""

    def __init__(self) -> None:
        # Modelo 3D genérico de una cara, expresado en milímetros.
        self.model_points_3d = np.array(
            [
                (0.0, 0.0, 0.0),       # Nariz
                (0.0, -63.6, -12.5),   # Mentón
                (-43.3, 32.7, -26.0),  # Ojo izquierdo
                (43.3, 32.7, -26.0),   # Ojo derecho
                (-28.9, -28.9, -24.1), # Boca izquierda
                (28.9, -28.9, -24.1),  # Boca derecha
            ],
            dtype=np.float64,
        )
        self.umbral_giro: float = 35.0
        self.landmark_indices = [1, 152, 33, 263, 61, 291]

    def estimar(
        self,
        frame_shape: tuple[int, int, int],
        face_landmarks: Any,
    ) -> tuple[bool, float, float]:
        """
        Calcula la orientación y devuelve (está_de_frente, yaw, pitch).

        ``face_landmarks`` debe ser el objeto de landmarks de una cara
        devuelto por MediaPipe Face Mesh.
        """
        alto, ancho = frame_shape[:2]

        # MediaPipe entrega coordenadas normalizadas entre 0.0 y 1.0.
        image_points_2d = np.array(
            [
                (
                    face_landmarks.landmark[indice].x * ancho,
                    face_landmarks.landmark[indice].y * alto,
                )
                for indice in self.landmark_indices
            ],
            dtype=np.float64,
        )

        # Aproximamos la cámara con una distancia focal igual al ancho.
        focal_length = float(ancho)
        camera_matrix = np.array(
            [
                [focal_length, 0.0, ancho / 2.0],
                [0.0, focal_length, alto / 2.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        # solvePnP encuentra la posición y rotación de la cara respecto
        # de la cámara a partir de los puntos 3D y sus proyecciones 2D.
        solucion_correcta, rotation_vector, _ = cv2.solvePnP(
            self.model_points_3d,
            image_points_2d,
            camera_matrix,
            dist_coeffs,
        )
        if not solucion_correcta:
            return False, 0.0, 0.0

        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        rq_result = cv2.RQDecomp3x3(rotation_matrix)
        # OpenCV devuelve los ángulos como primer resultado. Algunas
        # versiones agregan valores adicionales después de ese resultado.
        euler_angles = rq_result[0]

        # RQDecomp3x3 devuelve los ángulos en el orden:
        # pitch (X), yaw (Y) y roll (Z).
        pitch = float(euler_angles[0])
        yaw = float(euler_angles[1])

        esta_de_frente = abs(yaw) <= self.umbral_giro
        return esta_de_frente, yaw, pitch
