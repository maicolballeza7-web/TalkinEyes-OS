import tkinter as tk
from typing import Callable

from calibration.calibration import Calibrador
from calibration.user_profile import UserProfile
from core.ear import calcular_ear_promedio
from core.landmarks import LandmarksExtractor


class CalibrationUI:
    """Muestra y ejecuta las fases de calibración del usuario."""

    def __init__(
        self,
        ventana: tk.Tk,
        camara,
        detector,
        on_terminado: Callable[[], None],
    ) -> None:
        # Guardamos las dependencias que usaremos durante la calibración.
        self.ventana = ventana
        self.camara = camara
        self.detector = detector
        self.on_terminado = on_terminado

        # Creamos los objetos que almacenan y guardan los datos del usuario.
        self.calibrador = Calibrador()
        self.perfil = UserProfile()
        self.extractor = LandmarksExtractor()

        # La fase 0 es ojos abiertos y la fase 1 es ojos cerrados.
        self.fase: int = 0
        self.frames_fase: int = 0
        self.timer_id = None

        # Este label muestra las instrucciones al usuario.
        self.instrucciones = tk.Label(
            ventana,
            text="",
            font=("Arial", 28, "bold"),
            bg="#F4F7FB",
            fg="#263238",
            wraplength=700,
        )

    def iniciar(self) -> None:
        """Muestra las instrucciones y comienza la captura de frames."""
        # Reiniciamos el progreso para permitir otra calibración.
        self.fase = 0
        self.frames_fase = 0
        self.calibrador.ears_abiertos.clear()
        self.calibrador.ears_cerrados.clear()

        self.instrucciones.config(text="Mira normal a la cámara")
        self.instrucciones.pack(expand=True, fill="both")
        self._bucle()

    def _bucle(self) -> None:
        """Captura un frame y guarda su EAR según la fase actual."""
        frame = self.camara.read()

        if frame is not None:
            self.frames_fase += 1
            resultados = self.detector.detect(frame)
            ojo_izquierdo = self.extractor.extraer_ojo_izquierdo(resultados)
            ojo_derecho = self.extractor.extraer_ojo_derecho(resultados)
            alto, ancho, _ = frame.shape
            ear = calcular_ear_promedio(
                ojo_izquierdo,
                ojo_derecho,
                ancho,
                alto,
            )

            # Solo contamos frames con un EAR válido.
            if ear is not None:
                if self.fase == 0:
                    self.calibrador.agregar_abierto(ear)
                elif self.fase == 1:
                    self.calibrador.agregar_cerrado(ear)

        # Cada fase termina después de capturar 100 frames.
        if self.frames_fase >= 100:
            if self.fase == 0:
                self.fase = 1
                self.frames_fase = 0
                self.instrucciones.config(text="Cierra los ojos")
            else:
                self.fase = 2
                self.frames_fase = 0
                self._finalizar()
                return

        # Esperamos aproximadamente 30 ms antes de capturar el siguiente frame.
        self.timer_id = self.ventana.after(30, self._bucle)

    def _finalizar(self) -> None:
        """Calcula, guarda y comunica los resultados de la calibración."""
        umbral_cierre, umbral_reapertura = self.calibrador.calcular_umbrales()

        # Guardamos los promedios y umbrales en el perfil del usuario.
        if self.calibrador.ears_abiertos:
            self.perfil.ear_baseline = sum(
                self.calibrador.ears_abiertos
            ) / len(self.calibrador.ears_abiertos)
        if self.calibrador.ears_cerrados:
            self.perfil.ear_closed = sum(
                self.calibrador.ears_cerrados
            ) / len(self.calibrador.ears_cerrados)

        self.perfil.umbral_cierre = umbral_cierre
        self.perfil.umbral_reapertura = umbral_reapertura
        self.perfil.guardar()

        self.instrucciones.config(text="¡Listo!")
        self.on_terminado()