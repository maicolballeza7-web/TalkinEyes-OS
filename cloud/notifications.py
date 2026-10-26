"""Notificador simulado de alertas prioritarias para TalkinEyes."""

import json
from datetime import datetime


class EmergencyNotifier:
    """Simula el envío de alertas a un tópico de AWS SNS."""

    def __init__(
        self,
        topic_arn: str = (
            "arn:aws:sns:us-east-1:123456789012:TalkinEyesAlert"
        ),
    ) -> None:
        self.topic_arn = topic_arn

    def enviar_alerta(self, mensaje: str) -> bool:
        """Imprime una alerta con formato SNS y confirma su envío simulado."""
        alerta = {
            "timestamp": datetime.now().isoformat(),
            "topic": self.topic_arn,
            "mensaje": mensaje,
            "estado": "enviada",
        }
        alerta_json = json.dumps(alerta, indent=4, ensure_ascii=False)

        print("\n" + "=" * 60)
        print("🚨 ALERTA AWS ENVIADA 🚨")
        print("=" * 60)
        print(alerta_json)
        print("=" * 60 + "\n")

        return True
