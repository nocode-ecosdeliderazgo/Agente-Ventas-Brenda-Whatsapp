import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'xd')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+14155238886')  # Actualizar con tu nuevo número

DATABASE_URL = os.getenv('DATABASE_URL', '')
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', '')
SMTP_PORT = os.getenv('SMTP_PORT', '')
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
ADVISOR_EMAIL = os.getenv('ADVISOR_EMAIL', '')

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    raise EnvironmentError("Faltan variables de entorno de Twilio. Verifica tu .env")

# TODO: Adaptar para recibir mensajes entrantes vía webhook de Twilio 