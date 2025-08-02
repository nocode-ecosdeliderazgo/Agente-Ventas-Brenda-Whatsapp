#!/usr/bin/env python3
"""
Script para cambiar webhooks de Twilio entre desarrollo y producción
"""
import os
import requests
import json
from pathlib import Path

# Cargar variables de entorno
def load_env():
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value.strip('"')

def get_ngrok_url():
    """Obtiene la URL de ngrok si está ejecutándose"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        if response.status_code == 200:
            tunnels = response.json()["tunnels"]
            for tunnel in tunnels:
                if tunnel["proto"] == "https":
                    return tunnel["public_url"]
    except:
        pass
    return None

def update_twilio_webhook(webhook_url, environment):
    """Actualiza el webhook de Twilio"""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    if not account_sid or not auth_token:
        print("❌ Error: TWILIO_ACCOUNT_SID o TWILIO_AUTH_TOKEN no configurados")
        return False
    
    if not whatsapp_number:
        print("❌ Error: TWILIO_PHONE_NUMBER no configurado en .env")
        return False
    
    print(f"🔍 Configurando webhook para WhatsApp Sandbox")
    print(f"📱 Número: {whatsapp_number}")
    
    # Para WhatsApp Sandbox, usamos la API de Messaging Services
    # Primero, obtener los servicios de mensajería
    url = f"https://messaging.twilio.com/v1/Services"
    response = requests.get(url, auth=(account_sid, auth_token))
    
    if response.status_code == 200:
        response_data = response.json()
        services = response_data.get("data", [])
        print(f"📋 Servicios de mensajería encontrados: {len(services)}")
        
        # Mostrar todos los servicios para debug
        for i, service in enumerate(services):
            print(f"   {i+1}. {service.get('friendly_name', 'N/A')} (SID: {service.get('sid', 'N/A')})")
        
        # Buscar el servicio de WhatsApp Sandbox
        whatsapp_service = None
        for service in services:
            service_name = service.get("friendly_name", "").lower()
            if "whatsapp" in service_name or "sandbox" in service_name:
                whatsapp_service = service
                print(f"✅ Servicio WhatsApp encontrado: {service.get('friendly_name')}")
                break
        
        if not whatsapp_service:
            print("❌ No se encontró servicio de WhatsApp Sandbox")
            print("💡 Asegúrate de haber configurado el WhatsApp Sandbox en Twilio Console")
            print("💡 Alternativa: Configura manualmente el webhook en Twilio Console")
            return False
        
        # Actualizar el webhook del servicio
        service_sid = whatsapp_service["sid"]
        update_url = f"https://messaging.twilio.com/v1/Services/{service_sid}"
        
        data = {
            "InboundRequestUrl": webhook_url,
            "InboundMethod": "POST"
        }
        
        response = requests.post(update_url, auth=(account_sid, auth_token), data=data)
        
        if response.status_code == 200:
            print(f"✅ Webhook actualizado a {environment}: {webhook_url}")
            return True
        else:
            print(f"❌ Error actualizando webhook: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
    else:
        print(f"❌ Error obteniendo servicios: {response.status_code}")
        print(f"📋 Respuesta: {response.text}")
        return False

def main():
    """Función principal"""
    print("🔄 TWILIO WEBHOOK SWITCHER")
    print("=" * 40)
    
    # Cargar variables de entorno
    load_env()
    
    print("🎯 Selecciona el entorno:")
    print("1. Desarrollo (ngrok)")
    print("2. Producción (Heroku)")
    print("3. Verificar ngrok")
    print("4. Configurar manualmente")
    
    choice = input("\nOpción (1-4): ").strip()
    
    if choice == "1":
        # Desarrollo con ngrok
        ngrok_url = get_ngrok_url()
        if not ngrok_url:
            # Usar URL fija si ngrok no está ejecutándose
            ngrok_url = "https://cute-kind-dog.ngrok-free.app"
            print(f"⚠️ ngrok no detectado, usando URL fija: {ngrok_url}")
        
        webhook_url = ngrok_url
        environment = "DESARROLLO"
        
    elif choice == "2":
        # Producción con Heroku
        webhook_url = "https://brenda-whatsapp-bot-f1bace3c0d6e.herokuapp.com/webhook"
        environment = "PRODUCCIÓN"
        
    elif choice == "3":
        # Verificar ngrok
        ngrok_url = get_ngrok_url()
        if ngrok_url:
            print(f"✅ ngrok ejecutándose: {ngrok_url}")
        else:
            print("❌ ngrok no está ejecutándose")
            print("💡 Ejecuta: ngrok http 8000")
            print("📝 URL fija disponible: https://cute-kind-dog.ngrok-free.app")
        return
        
    elif choice == "4":
        # Configuración manual
        print("\n📋 URLs disponibles:")
        print("🔄 Desarrollo: https://cute-kind-dog.ngrok-free.app")
        print("🚀 Producción: https://brenda-whatsapp-bot-f1bace3c0d6e.herokuapp.com/webhook")
        print("\n💡 Para configurar manualmente:")
        print("1. Ve a Twilio Console → Messaging → Settings → WhatsApp Sandbox")
        print("2. En 'When a message comes in', pon la URL que quieras usar")
        print("3. Click en 'Save'")
        return
    
    else:
        print("❌ Opción inválida")
        return
    
    print(f"\n🔄 Cambiando a {environment}...")
    print(f"📡 URL: {webhook_url}")
    
    # Confirmar cambio
    confirm = input("\n¿Confirmar cambio? (y/N): ").strip().lower()
    if confirm != "y":
        print("❌ Cambio cancelado")
        return
    
    # Actualizar webhook
    if update_twilio_webhook(webhook_url, environment):
        print(f"\n🎉 ¡Webhook cambiado exitosamente a {environment}!")
        print(f"📱 Ahora puedes probar desde WhatsApp")
        
        if environment == "DESARROLLO":
            print("\n💡 Para probar desarrollo:")
            print("1. Ejecuta: python run_development.py")
            print("2. Envía mensaje desde WhatsApp")
        elif environment == "PRODUCCIÓN":
            print("\n💡 Para probar producción:")
            print("1. El servidor ya está funcionando en Heroku")
            print("2. Envía mensaje desde WhatsApp")
    else:
        print("\n❌ Error cambiando webhook")

if __name__ == "__main__":
    main() 