"""
user_profile.py
---------------
Representa el perfil de calibración personalizada de un usuario.
Sabe cómo guardarse y cargarse desde un archivo JSON.

FASE: Semana 2 (Personalized Calibration)
"""

import json
import os


class UserProfile:
    """Guarda los parámetros de calibración de un usuario específico."""

    def __init__(self, ruta_archivo: str = "perfil_usuario.json") -> None:
        self.ruta_archivo = ruta_archivo

        # Datos del perfil con valores por defecto universales.
        self.ear_baseline: float = 0.28
        self.ear_closed: float = 0.10
        self.umbral_cierre: float = 0.16
        self.umbral_reapertura: float = 0.28

    def guardar(self) -> bool:
        """Guarda el perfil actual en el disco."""
        datos: dict[str, float] = {
            "ear_baseline": self.ear_baseline,
            "ear_closed": self.ear_closed,
            "umbral_cierre": self.umbral_cierre,
            "umbral_reapertura": self.umbral_reapertura,
        }

        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=4)
            return True
        except OSError:
            return False

    def cargar(self) -> bool:
        """Intenta cargar un perfil del disco."""
        if not os.path.exists(self.ruta_archivo):
            return False

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            # Actualizamos los atributos con los datos del archivo.
            self.ear_baseline = datos.get("ear_baseline", 0.28)
            self.ear_closed = datos.get("ear_closed", 0.10)
            self.umbral_cierre = datos.get("umbral_cierre", 0.16)
            self.umbral_reapertura = datos.get("umbral_reapertura", 0.28)
            return True
        except (OSError, json.JSONDecodeError):
            return False
