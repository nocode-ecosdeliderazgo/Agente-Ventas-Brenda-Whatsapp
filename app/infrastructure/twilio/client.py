"""
Cliente de Twilio para envío de mensajes de WhatsApp.
Capa de infraestructura que maneja la comunicación con la API de Twilio.
"""
import logging
from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from app.config import settings
from app.domain.entities.message import OutgoingMessage, MessageType

logger = logging.getLogger(__name__)


class TwilioWhatsAppClient:
    """Cliente especializado para WhatsApp via Twilio."""
    
    def __init__(self):
        """Inicializa el cliente de Twilio."""
        self.client = Client(
            settings.twilio_account_sid, 
            settings.twilio_auth_token
        )
        self.from_number = f"whatsapp:{settings.twilio_phone_number}"
        
    async def send_message(self, message: OutgoingMessage) -> Dict[str, Any]:
        """
        Envía un mensaje de WhatsApp.
        
        Args:
            message: Mensaje a enviar
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Preparar datos para Twilio
            twilio_data = {
                'body': message.body,
                'from_': self.from_number,
                'to': f'whatsapp:{message.to_number}'
            }
            
            # Agregar multimedia si existe
            if message.media_url:
                twilio_data['media_url'] = [message.media_url]
            
            # Enviar mensaje
            twilio_message = self.client.messages.create(**twilio_data)
            
            logger.info(f"Mensaje enviado exitosamente. SID: {twilio_message.sid}")
            
            return {
                'success': True,
                'message_sid': twilio_message.sid,
                'status': twilio_message.status,
                'to': message.to_number,
                'error': None
            }
            
        except TwilioException as e:
            logger.error(f"Error de Twilio enviando mensaje: {e}")
            return {
                'success': False,
                'message_sid': None,
                'status': 'failed',
                'to': message.to_number,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error inesperado enviando mensaje: {e}")
            return {
                'success': False,
                'message_sid': None,
                'status': 'failed', 
                'to': message.to_number,
                'error': str(e)
            }
    
    async def send_text(self, to_number: str, text: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto simple.
        
        Args:
            to_number: Número de teléfono destino
            text: Texto del mensaje
            
        Returns:
            Dict con el resultado del envío
        """
        message = OutgoingMessage(
            to_number=to_number,
            body=text,
            message_type=MessageType.TEXT
        )
        return await self.send_message(message)
    
    async def send_media(self, to_number: str, text: str, media_url: str) -> Dict[str, Any]:
        """
        Envía un mensaje con multimedia.
        
        Args:
            to_number: Número de teléfono destino
            text: Texto del mensaje
            media_url: URL del archivo multimedia
            
        Returns:
            Dict con el resultado del envío
        """
        message = OutgoingMessage(
            to_number=to_number,
            body=text,
            message_type=MessageType.IMAGE,  # Por ahora asumimos imagen
            media_url=media_url
        )
        return await self.send_message(message)
    
    def verify_webhook_signature(self, signature: str, url: str, params: Dict[str, Any]) -> bool:
        """
        Verifica la firma del webhook de Twilio para seguridad.
        
        Args:
            signature: Firma del webhook
            url: URL del webhook
            params: Parámetros del webhook
            
        Returns:
            True si la firma es válida
        """
        if not settings.webhook_verify_signature:
            return True
            
        try:
            from twilio.request_validator import RequestValidator
            validator = RequestValidator(settings.twilio_auth_token)
            return validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Error verificando firma del webhook: {e}")
            return False