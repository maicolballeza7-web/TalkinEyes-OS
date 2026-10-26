"""Historial local de selecciones para personalizar los menús."""

import json
import os


class UserHistory:
    """Registra selecciones y ordena opciones por frecuencia de uso."""

    def __init__(self, ruta_archivo: str = "historial.json") -> None:
        self.ruta_archivo = ruta_archivo
        self.frecuencias: dict[str, int] = {}
        self._cargar()

    def _cargar(self) -> None:
        """Carga las frecuencias existentes cuando el archivo está disponible."""
        if not os.path.exists(self.ruta_archivo):
            return

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (OSError, json.JSONDecodeError):
            return

        if isinstance(datos, dict):
            self.frecuencias = {
                opcion: frecuencia
                for opcion, frecuencia in datos.items()
                if isinstance(opcion, str) and isinstance(frecuencia, int)
            }

    def registrar_seleccion(self, opcion: str) -> None:
        """Incrementa la frecuencia de una opción y guarda el historial."""
        self.frecuencias[opcion] = self.frecuencias.get(opcion, 0) + 1
        with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(self.frecuencias, archivo, indent=4, ensure_ascii=False)

    def ordenar_opciones(self, opciones_originales: list[str]) -> list[str]:
        """Devuelve las opciones ordenadas de mayor a menor frecuencia."""
        return sorted(
            opciones_originales,
            key=lambda opcion: self.frecuencias.get(opcion, 0),
            reverse=True,
        )
