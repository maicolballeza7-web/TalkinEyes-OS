class BlinkEngine:
    """Detecta parpadeos a partir del valor EAR de cada frame."""

    def __init__(self) -> None:
        # Definimos los valores que controlan cuándo el ojo se cierra y se abre.
        self.umbral_cierre: float = 0.16
        self.umbral_reapertura: float = 0.28
        self.frames_minimos: int = 10
        self.min_ear_actual: float = 1.0
        self.ultimo_blink_frames: int = 0
        self.ultimo_blink_ear: float = 1.0
    
        # Al comenzar, suponemos que el ojo está abierto.
        self.estado_anterior: str = "abierto"
        self.frames_cerrados: int = 0

    def procesar(self, ear: float) -> bool:
        """Procesa un frame y devuelve True si se completó un parpadeo."""
        # Guardamos cuántos frames llevaba cerrado antes de este frame.
        frames_previos: int = self.frames_cerrados

        # Decidimos el estado actual usando el estado anterior y el valor EAR.
        if self.estado_anterior == "abierto" and ear < self.umbral_cierre:
            estado_actual: str = "cerrado"
        elif (
            self.estado_anterior == "cerrado"
            and ear > self.umbral_reapertura
        ):
            estado_actual = "abierto"
        else:
            estado_actual = self.estado_anterior

        # Contamos los frames consecutivos en los que el ojo está cerrado.
        if estado_actual == "cerrado":
            self.frames_cerrados += 1
            self.min_ear_actual = min(self.min_ear_actual, ear)  # Guardamos el más bajo
        else:
            self.frames_cerrados = 0

        # Un parpadeo termina al reabrir el ojo después del tiempo mínimo.
        hubo_parpadeo: bool = (
            self.estado_anterior == "cerrado"
            and estado_actual == "abierto"
            and frames_previos >= self.frames_minimos
        )

        # Guardamos los datos del parpadeo para calcular su confianza después.
        if hubo_parpadeo:
            self.ultimo_blink_frames = frames_previos
            self.ultimo_blink_ear = self.min_ear_actual  # Usamos el más bajo
            self.min_ear_actual = 1.0  # Reiniciamos para el próximo
        elif estado_actual == "abierto" and self.estado_anterior == "cerrado":
            self.min_ear_actual = 1.0  # Si fue un parpadeo rápido, también reiniciamos

        # Guardamos el estado para procesar correctamente el siguiente frame.
        self.estado_anterior = estado_actual
        return hubo_parpadeo
