from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.config.settings import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        """Inicializar cliente Twilio con configuración unificada."""
        try:
            self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            logger.info("✅ Cliente Twilio inicializado correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente Twilio: {e}")
            raise

    def enviar_sms(self, to_number: str, mensaje: str) -> dict:
        """Enviar SMS usando número de Twilio configurado."""
        try:
            message = self.client.messages.create(
                body=mensaje,
                from_=settings.twilio_phone_number,
                to=to_number
            )
            logger.info(f"📱 SMS enviado exitosamente a {to_number}, SID: {message.sid}")
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'platform': 'sms',
                'to': to_number
            }
        except TwilioRestException as e:
            logger.error(f"❌ Error Twilio SMS a {to_number}: {e.msg} (Code: {e.code})")
            return {'success': False, 'error': f"Twilio Error {e.code}: {e.msg}", 'platform': 'sms'}
        except Exception as e:
            logger.exception(f"❌ Error inesperado enviando SMS a {to_number}")
            return {'success': False, 'error': str(e), 'platform': 'sms'}

    def enviar_whatsapp(self, to_number: str, mensaje: str) -> dict:
        """Enviar mensaje de WhatsApp usando número de Twilio configurado."""
        try:
            message = self.client.messages.create(
                body=mensaje,
                from_=f'whatsapp:{settings.twilio_phone_number}',
                to=f'whatsapp:{to_number}'
            )
            logger.info(f"📞 WhatsApp enviado exitosamente a {to_number}, SID: {message.sid}")
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'platform': 'whatsapp',
                'to': to_number
            }
        except TwilioRestException as e:
            logger.error(f"❌ Error Twilio WhatsApp a {to_number}: {e.msg} (Code: {e.code})")
            return {'success': False, 'error': f"Twilio Error {e.code}: {e.msg}", 'platform': 'whatsapp'}
        except Exception as e:
            logger.exception(f"❌ Error inesperado enviando WhatsApp a {to_number}")
            return {'success': False, 'error': str(e), 'platform': 'whatsapp'}

    # TODO: Agregar métodos para envío de multimedia y manejo de plantillas si es necesario 