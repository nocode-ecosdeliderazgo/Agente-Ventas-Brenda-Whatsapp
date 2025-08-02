#!/usr/bin/env python3
"""
Script para probar la conexión de WhatsApp Sandbox
"""
import os
import requests
from pathlib import Path

def load_env():
    """Cargar variables de entorno"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value.strip('"')

def test_whatsapp_sandbox():
    """Probar la configuración del WhatsApp Sandbox"""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    print("🔍 PROBANDO CONFIGURACIÓN DE WHATSAPP SANDBOX")
    print("=" * 50)
    
    print(f"📋 Account SID: {account_sid}")
    print(f"📋 Auth Token: {auth_token[:10]}...")
    print(f"📱 Número: {phone_number}")
    
    # Probar credenciales
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}.json"
    response = requests.get(url, auth=(account_sid, auth_token))
    
    if response.status_code == 200:
        print("✅ Credenciales válidas")
        account_info = response.json()
        print(f"📋 Cuenta: {account_info.get('friendly_name', 'N/A')}")
        print(f"📋 Estado: {account_info.get('status', 'N/A')}")
    else:
        print(f"❌ Error con credenciales: {response.status_code}")
        return False
    
    # Probar envío de mensaje de prueba
    print("\n📤 Probando envío de mensaje...")
    
    # URL para enviar mensajes de WhatsApp
    send_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    
    # Datos del mensaje de prueba
    data = {
        "From": f"whatsapp:{phone_number}",
        "To": "whatsapp:+5215614686075",  # Tu número de WhatsApp
        "Body": "🤖 Hola! Este es un mensaje de prueba desde Brenda WhatsApp Bot"
    }
    
    response = requests.post(send_url, auth=(account_sid, auth_token), data=data)
    
    if response.status_code == 201:
        message_info = response.json()
        print("✅ Mensaje enviado correctamente")
        print(f"📋 SID del mensaje: {message_info.get('sid')}")
        print(f"📋 Estado: {message_info.get('status')}")
        return True
    else:
        print(f"❌ Error enviando mensaje: {response.status_code}")
        print(f"📋 Respuesta: {response.text}")
        return False

def check_webhook_status():
    """Verificar el estado del webhook"""
    print("\n🔗 VERIFICANDO WEBHOOK")
    print("=" * 30)
    
    webhook_url = "https://brenda-whatsapp-bot-f1bace3c0d6e.herokuapp.com/webhook"
    
    try:
        response = requests.get(webhook_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Webhook accesible: {webhook_url}")
            return True
        else:
            print(f"⚠️  Webhook responde con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo al webhook: {e}")
        print("💡 Asegúrate de que ngrok esté ejecutándose")
        return False

def main():
    """Función principal"""
    print("🧪 WHATSAPP SANDBOX TESTER")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_env()
    
    # Probar configuración
    if test_whatsapp_sandbox():
        print("\n🎉 ¡Configuración correcta!")
        
        # Verificar webhook
        if check_webhook_status():
            print("\n✅ Todo listo para recibir mensajes")
            print("💡 Ahora puedes enviar mensajes desde WhatsApp al número +1 415 523 8886")
            print("💡 Con el código: join adult-rocket")
        else:
            print("\n⚠️  Webhook no accesible")
            print("💡 Ejecuta: ngrok http 8000")
    else:
        print("\n❌ Hay problemas con la configuración")
        print("💡 Verifica las credenciales en tu archivo .env")

if __name__ == "__main__":
    main() 