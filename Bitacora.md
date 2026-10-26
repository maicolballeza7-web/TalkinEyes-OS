📅 Bitácora de Desarrollo (Devlog) - TalkinEyes OS
🗓️ Semana 1: De Prototipo a Arquitectura
Días 1-2: Cimientos y Visión Core

Migración de V1 a V2 (OS): Se abandonó el código monolítico inicial y se creó una estructura modular orientada a objetos (POO).

Pipeline Visual: Se implementaron las clases Camera, FaceDetector y LandmarksExtractor.

Cálculo del EAR: Se separó la lógica matemática en ear.py, protegiéndola contra frames sin detección facial (evitando crasheos).

Días 3-4: El Motor de Parpadeos y Calibración

BlinkEngine: Se implementó una máquina de estados con histéresis para diferenciar parpadeos naturales de intencionales.

Calibración: Se creó el flujo para que el sistema aprenda los umbrales del usuario (Calibrador y UserProfile), guardándolos en un JSON local.

Text-to-Speech (TTS): Se aisló la voz en un hilo secundario (threading + queue) para evitar que la interfaz de Tkinter se congelara.

Día 5-6: Rediseño de Interfaz (UI)

Se creó la clase genérica Menu, eliminando el código duplicado de los 5 menús de la V1.

Se implementó el diseño visual con esquinas redondeadas, sombras y halos de selección usando Tkinter Canvas.

🗓️ Semana 2: Inteligencia, Robustez y Nube
Días 7-8: Capas de Seguridad

ConfidenceCalculator: Se añadió una capa de seguridad que evalúa la duración y profundidad del parpadeo. Si la confianza es menor al 50%, la selección se ignora.

HeadPoseEstimator: Implementación de visión 3D con OpenCV (cv2.solvePnP) para detectar si el usuario voltea la cabeza y pausar la interacción (se solucionaron bugs de API en OpenCV 4.11).

Cooldown y Confirmación: Se agregó un tiempo de espera de 1.5s para evitar dobles selecciones y un menú de "¿Confirmar? [SÍ/NO]" antes de hablar.

Días 9-10: IA Predictiva y Cloud

UserHistory (Predictive Menu): El sistema ahora guarda en un JSON las opciones más seleccionadas y las reordena automáticamente al inicio del menú para ahorrar esfuerzo al usuario.

EmergencyNotifier: Se implementó el componente en la nube. El botón de emergencia envía un JSON estructurado simulando una alerta a AWS SNS.

Día 11 (Hoy): Estabilización y Documentación

Corrección de bugs críticos (reinicio de estado al perder el rostro, ajustes en la cola de voz).

Rediseño del HUD para mostrar el estado del rastreador en tiempo real.

Redacción del README final y la documentación de arquitectura.

