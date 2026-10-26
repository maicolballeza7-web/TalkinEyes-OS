"""Cálculo de confianza para determinar si un parpadeo fue intencional."""


class ConfidenceCalculator:
    """Calcula la confianza de que un parpadeo fue intencional."""

    def __init__(self) -> None:
        self.frames_minimos: int = 10

 
    def calcular(self, frames_cerrados: int, ear_promedio_cierre: float) -> float:
        if frames_cerrados < self.frames_minimos:
            return 0.0

        # Si dura 15 frames, ya es un 100% de tiempo.
        score_tiempo: float = min(1.0, frames_cerrados / 15.0)
        
        # Si el ojo baja a 0.08, da 0.5. Si baja a 0.04, da 0.75. Es más justo.
        score_profundidad: float = max(0.0, 1.0 - (ear_promedio_cierre / 0.16))

        return (score_tiempo + score_profundidad) / 2.0
