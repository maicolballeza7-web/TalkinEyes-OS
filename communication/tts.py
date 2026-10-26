"""
tts.py
------
Convierte texto a voz usando pyttsx3.

Usa un hilo en segundo plano y una cola para que la voz no congele
la interfaz gráfica de Tkinter.

FASE: Semana 2, Días 10-11 (Módulo de comunicación)
"""

from __future__ import annotations

import queue
import threading

import pyttsx3

try:
    import pythoncom
except ImportError:
    pythoncom = None


class TextToSpeech:
    """Gestiona la voz del sistema sin bloquear la interfaz principal."""

    def __init__(self) -> None:
        # La cola guarda los textos que queremos decir.
        self.cola: queue.Queue[str | None] = queue.Queue()

        # El hilo daemon termina automáticamente cuando se cierra la aplicación.
        self.hilo = threading.Thread(target=self._worker, daemon=True)
        self.hilo.start()

    def hablar(self, texto: str) -> None:
        """Agrega un texto a la cola para que sea hablado."""
        self.cola.put(texto)


    def _worker(self) -> None:
        """Método privado que corre en segundo plano leyendo la cola."""
        if pythoncom is not None:
            pythoncom.CoInitialize()

        while True:
            # .get() se queda esperando hasta que haya algo en la cola.
            texto = self.cola.get()

            # Si recibimos None, significa "ciérrate".
            if texto is None:
                break

            try:
                # Como en la V1: creamos el motor, hablamos y lo destruimos.
                motor = pyttsx3.init()
                motor.setProperty("rate", 165)
                motor.say(texto)
                motor.runAndWait()
                motor.stop()
                del motor
            except Exception as e:
                print(f"Error de voz: {e}")

    def detener(self) -> None:
        """Apaga el hilo de voz de forma segura."""
        self.cola.put(None)
