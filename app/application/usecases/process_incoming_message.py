"""
Caso de uso para procesar mensajes entrantes de WhatsApp.
"""
import logging
from typing import Dict, Any

from app.domain.entities.message import IncomingMessage, OutgoingMessage, MessageType
from app.infrastructure.twilio.client import TwilioWhatsAppClient

logger = logging.getLogger(__name__)


class ProcessIncomingMessageUseCase:
    """Caso de uso para procesar mensajes entrantes y generar respuestas."""
    
    def __init__(self, twilio_client: TwilioWhatsAppClient):
        """
        Inicializa el caso de uso.
        
        Args:
            twilio_client: Cliente de Twilio para envío de respuestas
        """
        self.twilio_client = twilio_client
    
    async def execute(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un mensaje entrante y envía una respuesta automática.
        
        Args:
            webhook_data: Datos del webhook de Twilio
            
        Returns:
            Dict con el resultado del procesamiento
        """
        try:
            # Crear entidad de mensaje entrante
            incoming_message = IncomingMessage.from_twilio_webhook(webhook_data)
            
            logger.info(
                f"📨 Mensaje recibido de {incoming_message.from_number}: "
                f"'{incoming_message.body}'"
            )
            
            # Solo procesar mensajes de WhatsApp (ignorar SMS por ahora)
            if not incoming_message.is_whatsapp():
                logger.info("📱 Mensaje no es de WhatsApp, ignorando...")
                return {
                    'success': True,
                    'processed': False,
                    'reason': 'not_whatsapp'
                }
            
            # Generar respuesta automática
            response_text = self._generate_auto_response(incoming_message)
            
            # Crear mensaje de respuesta
            response_message = OutgoingMessage(
                to_number=incoming_message.from_number,
                body=response_text,
                message_type=MessageType.TEXT
            )
            
            # Enviar respuesta
            send_result = await self.twilio_client.send_message(response_message)
            
            if send_result['success']:
                logger.info(
                    f"✅ Respuesta enviada a {incoming_message.from_number}. "
                    f"SID: {send_result['message_sid']}"
                )
            else:
                logger.error(
                    f"❌ Error enviando respuesta: {send_result['error']}"
                )
            
            return {
                'success': True,
                'processed': True,
                'incoming_message': {
                    'from': incoming_message.from_number,
                    'body': incoming_message.body,
                    'message_sid': incoming_message.message_sid
                },
                'response_sent': send_result['success'],
                'response_sid': send_result.get('message_sid'),
                'response_text': response_text
            }
            
        except Exception as e:
            logger.error(f"💥 Error procesando mensaje entrante: {e}")
            return {
                'success': False,
                'processed': False,
                'error': str(e)
            }
    
    def _generate_auto_response(self, incoming_message: IncomingMessage) -> str:
        """
        Genera una respuesta automática para cualquier mensaje.
        
        Args:
            incoming_message: Mensaje entrante
            
        Returns:
            Texto de respuesta
        """
        # Por ahora, siempre responder "Hola" sin importar el mensaje
        return "Hola"
        
        # En el futuro aquí podemos agregar lógica más sofisticada:
        # - Análisis de intención
        # - Respuestas contextuales
        # - Integración con IA
        # - Sistema de memoria de usuario