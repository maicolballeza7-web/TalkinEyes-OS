"""Camera capture abstraction for TalkinEyes OS.

This module only owns opening, reading, and releasing an OpenCV camera.
It intentionally contains no MediaPipe or user-interface logic.
"""

from __future__ import annotations

from typing import Any

import cv2


class Camera:
    """Open and manage a single OpenCV video-capture device."""
    #se guarda el indice de la camara 0= la principal
    def __init__(self, camera_index: int = 0) -> None:
        self.camera_index = camera_index
        self._capture: Any | None = None
     # Pregunta: ¿la cámara está abierta? Devuelve True o False.
    @property
    def is_opened(self) -> bool:
        """Return whether the camera is currently open."""
        return self._capture is not None and self._capture.isOpened()
    #se abre la camara si todo sale bien 
    def open(self) -> None:
        """Open the configured camera or raise an explicit error."""
        if self.is_opened:
            return
    
        self._capture = cv2.VideoCapture(self.camera_index)
        #si hay un error se arroja un runtaim eror
        if not self._capture.isOpened():
            self.release()
            raise RuntimeError(
                f"Unable to open camera with index {self.camera_index}."
            )
    #Antes de leer la camara verifica que este abierta 
    def read(self) -> Any:
        """Read and return one BGR frame from the camera."""
        if not self.is_opened:
            raise RuntimeError("Camera must be opened before reading frames.")
        
        success, frame = self._capture.read()
        # Si falló la lectura del frame, lanzamos error.
        if not success:
            raise RuntimeError("Unable to read a frame from the camera.")
        #si no hay errores regresamos el frame capturado
        return frame
    #aquie cerramos la camara y liberamos recursos
    def release(self) -> None:
        """Release the camera resources if they are allocated."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None
    #aqui no etoy seguro pero creo que es un comando para abrir la camara
    def __enter__(self) -> Camera:
        """Open the camera for use in a context manager."""
        self.open()
        return self
    #lo mismo que el anterior pero para cerrar la camara
    def __exit__(self, *_: object) -> None:
        """Release the camera when leaving a context manager."""
        self.release()
