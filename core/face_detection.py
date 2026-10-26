"""Future responsibility: detect and localize faces in video frames."""

from __future__ import annotations

from typing import Any

import cv2
import mediapipe as mp


class FaceDetector:
    """
    Envuelve MediaPipe FaceMesh en una clase simple.

    Uso:
        detector = FaceDetector()
        resultados = detector.detect(frame)
        if resultados.multi_face_landmarks:
            # hay una cara
    """

    def __init__(
        self,
        max_num_faces: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        # max_num_faces=1 → solo queremos una cara (el usuario).
        # Las confidencias son umbrales de MediaPipe: qué tan seguro
        # debe estar para decir "sí, aquí hay una cara".
        # 0.5 es un valor intermedio razonable.
        self.max_num_faces = max_num_faces
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        # Creamos el objeto de MediaPipe FaceMesh.
        # refine_landmarks=True → activa landmarks más finos (incluye iris).
        # Es lo que usabas en V1.
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=self.max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )

    def detect(self, frame_bgr: Any) -> Any:
        """
        Recibe un frame en formato BGR (como lo da OpenCV).
        Devuelve los resultados de MediaPipe.

        Importante: MediaPipe espera RGB, no BGR.
        Por eso convertimos antes de procesar.
        """
        # Convertimos BGR -> RGB (MediaPipe lo requiere).
        # cv2.cvtColor crea un array NUEVO y contiguo en memoria.
        # MediaPipe exige esto (con el truco [:, :, ::-1] se rompe).    
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        # Le decimos a MediaPipe que no modifique el frame
        # (es una optimización de rendimiento, lo hacías en V1).
        frame_rgb.flags.writeable = False

        # Procesamos el frame: aquí es donde ocurre la magia.
        resultados = self._face_mesh.process(frame_rgb)

        return resultados

    def close(self) -> None:
        """Libera los recursos de MediaPipe."""
        self._face_mesh.close()
