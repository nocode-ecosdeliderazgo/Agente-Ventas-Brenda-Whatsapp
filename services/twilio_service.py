from twilio.rest import Client
from config.twilio_settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from datetime import datetime

class TwilioService:
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    def enviar_sms(self, to_number: str, mensaje: str) -> dict:
        try:
            message = self.client.messages.create(
                body=mensaje,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number
            )
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'platform': 'sms',
                'to': to_number
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'platform': 'sms'}

    def enviar_whatsapp(self, to_number: str, mensaje: str) -> dict:
        try:
            message = self.client.messages.create(
                body=mensaje,
                from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
                to=f'whatsapp:{to_number}'
            )
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'platform': 'whatsapp',
                'to': to_number
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'platform': 'whatsapp'}

# TODO: Agregar métodos para envío de multimedia y manejo de plantillas si es necesario 