"""
Caso de uso para enviar mensaje "Hola Mundo" usando la nueva arquitectura.
"""
import logging
from datetime import datetime
from typing import Dict, Any

from app.domain.entities.message import OutgoingMessage, MessageType
from app.infrastructure.twilio.client import TwilioWhatsAppClient

logger = logging.getLogger(__name__)


class SendHelloWorldUseCase:
    """Caso de uso para enviar un mensaje de prueba 'Hola Mundo'."""
    
    def __init__(self, twilio_client: TwilioWhatsAppClient):
        """
        Inicializa el caso de uso.
        
        Args:
            twilio_client: Cliente de Twilio para envío de mensajes
        """
        self.twilio_client = twilio_client
    
    async def execute(self, to_number: str, platform: str = "whatsapp") -> Dict[str, Any]:
        """
        Ejecuta el envío del mensaje "Hola Mundo".
        
        Args:
            to_number: Número de teléfono destino (formato internacional)
            platform: Plataforma de envío ("whatsapp" o "sms")
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Crear mensaje personalizado
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            if platform.lower() == "whatsapp":
                message_body = (
                    "¡Hola Mundo desde WhatsApp! 🚀\n\n"
                    "Este mensaje fue enviado usando la nueva arquitectura limpia "
                    "del bot Brenda con Twilio.\n\n"
                    f"📅 Fecha: {timestamp}\n"
                    "🏗️ Arquitectura: Clean Architecture\n"
                    "🔧 Tecnología: Python + Twilio + Pydantic"
                )
            else:
                message_body = (
                    f"¡Hola Mundo! 🌟\n\n"
                    f"Mensaje de prueba desde la nueva arquitectura.\n"
                    f"Fecha: {timestamp}"
                )
            
            # Crear entidad de mensaje
            message = OutgoingMessage(
                to_number=to_number,
                body=message_body,
                message_type=MessageType.TEXT
            )
            
            logger.info(f"Enviando mensaje 'Hola Mundo' a {to_number} via {platform}")
            
            # Enviar mensaje usando el cliente de Twilio
            if platform.lower() == "whatsapp":
                result = await self.twilio_client.send_message(message)
            else:
                # Para SMS, ajustar el cliente (por ahora usamos WhatsApp)
                result = await self.twilio_client.send_message(message)
            
            # Agregar información adicional al resultado
            result.update({
                'platform': platform,
                'message_body': message_body,
                'timestamp': timestamp,
                'use_case': 'SendHelloWorldUseCase'
            })
            
            if result['success']:
                logger.info(f"✅ Mensaje enviado exitosamente. SID: {result['message_sid']}")
            else:
                logger.error(f"❌ Error enviando mensaje: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en SendHelloWorldUseCase: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': platform,
                'to': to_number,
                'use_case': 'SendHelloWorldUseCase'
            }
    
    async def execute_sms(self, to_number: str) -> Dict[str, Any]:
        """Ejecuta el envío como SMS."""
        return await self.execute(to_number, "sms")
    
    async def execute_whatsapp(self, to_number: str) -> Dict[str, Any]:
        """Ejecuta el envío como WhatsApp."""
        return await self.execute(to_number, "whatsapp")