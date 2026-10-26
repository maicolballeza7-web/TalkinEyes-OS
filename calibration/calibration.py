import json
import os


class Calibrador:
    """Calcula y guarda los umbrales EAR de un usuario."""

    def __init__(self) -> None:
        self.ears_abiertos: list[float] = []
        self.ears_cerrados: list[float] = []
        self.ruta_archivo: str = "perfil_usuario.json"

    def agregar_abierto(self, ear: float) -> None:
        """Agrega un valor EAR medido con los ojos abiertos."""
        self.ears_abiertos.append(ear)

    def agregar_cerrado(self, ear: float) -> None:
        """Agrega un valor EAR medido con los ojos cerrados."""
        self.ears_cerrados.append(ear)

    def calcular_umbrales(self) -> tuple[float, float]:
        """Calcula los umbrales de cierre y reapertura."""
        # Necesitamos suficientes mediciones para hacer una calibración útil.
        if len(self.ears_abiertos) < 10 or len(self.ears_cerrados) < 10:
            return 0.16, 0.28

        prom_abierto: float = sum(self.ears_abiertos) / len(self.ears_abiertos)
        prom_cerrado: float = sum(self.ears_cerrados) / len(self.ears_cerrados)

        umbral_cierre: float = (
            prom_cerrado + (prom_abierto - prom_cerrado) * 0.3
        )
        umbral_reapertura: float = (
            prom_cerrado + (prom_abierto - prom_cerrado) * 0.7
        )

        return umbral_cierre, umbral_reapertura
