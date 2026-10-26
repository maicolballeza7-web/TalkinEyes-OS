"""
main.py
-------
Punto de entrada de TalkinEyes OS.
Une la visión, la detección de parpadeos, la interfaz y la voz.

FASE: Semana 2, Días 12-13 (Integración completa)
"""

import tkinter as tk
import time

import cv2
from PIL import Image, ImageTk

from cloud.notifications import EmergencyNotifier
from communication.tts import TextToSpeech
from core.blink_engine import BlinkEngine
from core.camera import Camera
from core.ear import calcular_ear_promedio
from core.face_detection import FaceDetector
from core.landmarks import LandmarksExtractor
from calibration.user_profile import UserProfile
from ui.calibration_view import CalibrationUI
from core.head_pose import HeadPoseEstimator
from core.confidence import ConfidenceCalculator
from intelligence.history import UserHistory
from ui.menu import Menu


class TalkinEyesApp:
    """La aplicación principal que une todos los módulos."""

    def __init__(self, ventana) -> None:
        self.ventana = ventana
        self.ventana.title("TalkinEyes OS")
        self.ventana.geometry("1000x600")
        self.ventana.configure(bg="#F0F4F8")

        # Iniciamos la cámara, la visión y la voz.
        self.camara = Camera(0)
        self.camara.open()
        self.detector = FaceDetector()
        self.extractor = LandmarksExtractor()
        self.head_pose = HeadPoseEstimator()
        self.confianza = ConfidenceCalculator()
        self.blink_engine = BlinkEngine()
        self.perfil = UserProfile()
        if self.perfil.cargar():
            print("✅ Perfil cargado. Aplicando umbrales personalizados.")
            self.blink_engine.umbral_cierre = self.perfil.umbral_cierre
            self.blink_engine.umbral_reapertura = self.perfil.umbral_reapertura
            print(f"Umbral cierre: {self.blink_engine.umbral_cierre:.3f}")
            print(f"Umbral reapertura: {self.blink_engine.umbral_reapertura:.3f}")
        else:
            print("⚠️ No hay perfil. Usando umbrales por defecto (0.16 / 0.28).")
            print("Ejecuta 'python -m ui.calibration_view' para calibrar.")
        self.voz = TextToSpeech()
        self.notificador = EmergencyNotifier()
        self.historial = UserHistory()
        self.esta_calibrando = False
        self.tiempo_ultimo_parpadeo = 0
        self.opcion_pendiente = ""

        # Mostramos la cámara en una esquina de la ventana.
        self.camara_label = tk.Label(
            self.ventana,
            bg="#1E293B",
            bd=2,
            relief="solid",
        )
        self.camara_label.place(x=20, y=20, width=220, height=165)

        self.status_label = tk.Label(
            self.ventana,
            text="🟢 Rastreo OK",
            font=("Arial", 12, "bold"),
            bg="#F0F4F8",
            fg="#1E293B",
            anchor="w",
        )
        self.status_label.place(x=20, y=195, width=220, height=30)
    

        # Ordenamos cada submenú usando el historial, manteniendo los colores.
        opc_comer = [
            "HAY ALGO DE COMER",
            "TENGO HAMBRE",
            "QUIERO TOMAR ALGO",
            "NO QUIERO COMER",
        ]
        col_comer = ["#e992a1", "#c9aa54", "#d2e67a", "#daa48b"]
        opc_comer, col_comer = self._ordenar_menu(opc_comer, col_comer)

        opc_bano = [
            "QUIERO IR AL BAÑO",
            "NECESITO PAPEL",
            "QUIERO LAVARME",
            "NO NECESITO IR",
        ]
        col_bano = ["#4D6594", "#8CAFEE", "#82CFFD", "#293C5E"]
        opc_bano, col_bano = self._ordenar_menu(opc_bano, col_bano)

        opc_dolor = [
            "ME DUELE LA CABEZA",
            "ME DUELE EL ESTÓMAGO",
            "ME DUELE EL PECHO",
            "ME SIENTO MAL",
        ]
        col_dolor = ["#FFB84D", "#F5A65B", "#FF8E6E", "#E992A1"]
        opc_dolor, col_dolor = self._ordenar_menu(opc_dolor, col_dolor)

        opc_dormir = [
            "TENGO SUEÑO",
            "QUIERO DORMIR",
            "NECESITO AYUDA",
            "NO TENGO SUEÑO",
        ]
        col_dormir = ["#63C687", "#78CFA0", "#86CFA5", "#A4DB96"]
        opc_dormir, col_dormir = self._ordenar_menu(opc_dormir, col_dormir)

        # Creamos los submenús verticales.
        self.menu_comer = Menu(
            ventana,
            "🍽️ COMER",
            opc_comer,
            col_comer,
            on_select=lambda indice: self._al_elegir_frase(indice, "comer"),
        )

        self.menu_bano = Menu(
            ventana,
            "🚿 BAÑO",
            opc_bano,
            col_bano,
            on_select=lambda indice: self._al_elegir_frase(indice, "bano"),
        )

        self.menu_dolor = Menu(
            ventana,
            "🩹 DOLOR",
            opc_dolor,
            col_dolor,
            on_select=lambda indice: self._al_elegir_frase(indice, "dolor"),
        )

        self.menu_dormir = Menu(
            ventana,
            "😴 DORMIR",
            opc_dormir,
            col_dormir,
            on_select=lambda indice: self._al_elegir_frase(indice, "dormir"),
        )

        self.menu_confirmacion = Menu(
            ventana,
            "¿Confirmar?",
            ["SÍ", "NO"],
            ["#63C687", "#E992A1"],
            on_select=self._resolver_confirmacion,
        )

        # Creamos el menú principal con diseño de cuadrícula.
        opc_principal = ["🍽️ COMER", "🚿 BAÑO", "🩹 DOLOR", "😴 DORMIR"]
        col_principal = ["#FF8E6E", "#6D9BF7", "#FFB84D", "#63C687"]
        opc_principal, col_principal = self._ordenar_menu(
            opc_principal,
            col_principal,
        )
        self.menu_principal = Menu(
            ventana,
            "TalkinEyes",
            opc_principal,
            col_principal,
            on_select=self._al_elegir_categoria,
            layout="cuadricula",
            subtitulo="Menú de asistencia",
        )

        self.btn_calibrar = tk.Button(
            self.ventana,
            text="⚙️ Calibrar",
            bg="#E2E8F0",
            fg="#1E293B",
            relief="flat",
            font=("Arial", 11, "bold"),
            command=self._iniciar_calibracion,
        )
        self.btn_calibrar.place(x=20, y=240, width=105, height=40)

        self.btn_emergencia = tk.Button(
            self.ventana,
            text="🆘 Ayuda",
            bg="#FEE2E2",
            fg="#991B1B",
            relief="flat",
            font=("Arial", 11, "bold"),
            command=self._emergencia,
        )
        self.btn_emergencia.place(x=135, y=240, width=105, height=40)

        # Mostramos el menú principal y comenzamos el bucle de cámara.
        self.menu_actual = self.menu_principal
        self.menu_actual.iniciar()

        self.ventana.protocol("WM_DELETE_WINDOW", self._cerrar)
        self._bucle_camara()

    def _ordenar_menu(self, opciones, colores):
        """Ordena opciones por historial manteniendo sus colores emparejados."""
        pares = list(zip(opciones, colores))
        pares.sort(
            key=lambda par: self.historial.frecuencias.get(par[0], 0),
            reverse=True,
        )
        opciones_ordenadas = [par[0] for par in pares]
        colores_ordenados = [par[1] for par in pares]
        return opciones_ordenadas, colores_ordenados

    def _emergencia(self) -> None:
        """Activa la comunicación local y la alerta AWS simulada."""
        print("🚨 EMERGENCIA ACTIVADA")
        self.voz.hablar("Necesito ayuda urgente.")
        self.notificador.enviar_alerta(
            "El usuario de TalkinEyes requiere asistencia inmediata."
        )
            
    def _iniciar_calibracion(self):
        """Pausa el juego y muestra la pantalla de calibración."""
        self.esta_calibrando = True
        self.menu_actual.detener()
        self.btn_calibrar.config(state="disabled")
        
        # Ocultamos la cámara
        self.camara_label.place_forget() 
        
        self.ui_calibracion = CalibrationUI(
            ventana=self.ventana,
            camara=self.camara,
            detector=self.detector,
            on_terminado=self._al_terminar_calibracion
        )
        self.ui_calibracion.iniciar()

    def _al_terminar_calibracion(self):
        """Se ejecuta cuando el usuario termina de calibrar."""
        print("✅ Calibración completada. Actualizando umbrales...")
        self.esta_calibrando = False
        
        self.perfil.cargar()
        self.blink_engine.umbral_cierre = self.perfil.umbral_cierre
        self.blink_engine.umbral_reapertura = self.perfil.umbral_reapertura
        
        self.ui_calibracion.instrucciones.pack_forget()
        self.camara_label.place(x=20, y=20, width=220, height=165)
        self.btn_calibrar.config(state="normal")
        
        self.menu_actual.detener()
        self.menu_confirmacion.detener()
        self.menu_actual = self.menu_principal
        self.menu_actual.iniciar()

    def _al_elegir_categoria(self, indice: int) -> None:
        """Se ejecuta cuando el usuario parpadea en el menú principal."""
        self.menu_principal.detener()

        menus = {
            "🍽️ COMER": self.menu_comer,
            "🚿 BAÑO": self.menu_bano,
            "🩹 DOLOR": self.menu_dolor,
            "😴 DORMIR": self.menu_dormir,
        }
        opcion = self.menu_principal.opciones[indice]
        self.menu_actual = menus[opcion]

        self.menu_actual.iniciar()

    def _al_elegir_frase(self, indice: int, categoria: str) -> None:
        """Se ejecuta cuando el usuario parpadea en un submenú."""
        # Buscamos el menú correspondiente para obtener el texto.
        menus = {
            "comer": self.menu_comer,
            "bano": self.menu_bano,
            "dolor": self.menu_dolor,
            "dormir": self.menu_dormir,
        }
        menu_usado = menus[categoria]
        frase = menu_usado.opciones[indice]

        print(f"Seleccionado: {frase}")
        menu_usado.detener()
        self.opcion_pendiente = frase
        self.menu_actual = self.menu_confirmacion
        self.menu_confirmacion.iniciar()

    def _resolver_confirmacion(self, indice: int) -> None:
        """Confirma o cancela la frase pendiente antes de comunicarla."""
        self.menu_confirmacion.detener()

        if indice == 0:
            frase = self.opcion_pendiente
            self.voz.hablar(frase)
            self.historial.registrar_seleccion(frase)

        self.opcion_pendiente = ""
        self.menu_actual = self.menu_principal
        self.menu_actual.iniciar()

    def _bucle_camara(self) -> None:
        """Lee la cámara y detecta parpadeos periódicamente."""
        frame = self.camara.read()

        if self.esta_calibrando:
            self.ventana.after(10, self._bucle_camara)
            return

        if frame is not None:
            # Procesamos la imagen para obtener los puntos de los ojos.
            resultados = self.detector.detect(frame)
            izq = self.extractor.extraer_ojo_izquierdo(resultados)
            der = self.extractor.extraer_ojo_derecho(resultados)
            alto, ancho, _ = frame.shape
            ear = calcular_ear_promedio(izq, der, ancho, alto)

            # Si tenemos una cara, verificamos si está de frente.
            esta_de_frente = False
            yaw = 0.0
            pitch = 0.0
            if resultados.multi_face_landmarks:
                cara = resultados.multi_face_landmarks[0]
                esta_de_frente, yaw, pitch = self.head_pose.estimar(
                    frame.shape,
                    cara,
                )
                if esta_de_frente:
                    self.status_label.config(
                        text=f"🟢 Yaw: {int(yaw)} | Pitch: {int(pitch)}",
                        bg="#F0F4F8",
                        fg="#1E293B",
                    )
                else:
                    self.status_label.config(
                        text=f"🔴 Gira: {int(yaw)} | Inclina: {int(pitch)}",
                        bg="#FEE2E2",
                        fg="#991B1B",
                    )
            else:
                self.status_label.config(
                    text="🔴 Sin rostro",
                    bg="#FEE2E2",
                    fg="#991B1B",
                )

            # Si no hay rostro, EAR o una orientación frontal válida,
            # descartamos cualquier parpadeo que estuviera en progreso.
            if (
                not resultados.multi_face_landmarks
                or ear is None
                or not esta_de_frente
            ):
                self.blink_engine.estado_anterior = "abierto"
                self.blink_engine.frames_cerrados = 0
                self.blink_engine.min_ear_actual = 1.0
            else:
                hubo_parpadeo = self.blink_engine.procesar(ear)
                if hubo_parpadeo:
                    conf = self.confianza.calcular(
                        self.blink_engine.ultimo_blink_frames,
                        self.blink_engine.ultimo_blink_ear
                    )
                    print(f"Parpadeo detectado. Frames: {self.blink_engine.ultimo_blink_frames}, EAR: {self.blink_engine.ultimo_blink_ear:.3f}, Confianza: {conf*100:.1f}%")
                    if conf >= 0.50:
                        print(f"¡Parpadeo válido! (Confianza: {conf*100:.1f}%)")
                        if time.time() - self.tiempo_ultimo_parpadeo > 1.5:
                            self.menu_actual.seleccionar()
                            self.tiempo_ultimo_parpadeo = time.time()

            # Convertimos el video de BGR a RGB y lo mostramos.
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen_tk = ImageTk.PhotoImage(
                Image.fromarray(frame_rgb).resize((240, 180))
            )
            self.camara_label.imgtk = imagen_tk
            self.camara_label.configure(image=imagen_tk)

        # Programamos el siguiente frame dentro de 10 milisegundos.
        self.ventana.after(10, self._bucle_camara)

    def _cerrar(self) -> None:
        """Cierra la cámara, la voz y la ventana."""
        self.camara.release()
        self.detector.close()
        self.voz.detener()
        self.ventana.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TalkinEyesApp(root)
    root.mainloop()
