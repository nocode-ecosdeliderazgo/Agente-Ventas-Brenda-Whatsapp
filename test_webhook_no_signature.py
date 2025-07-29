#!/usr/bin/env python3
"""
Script para probar el webhook sin verificación de firma.
"""
import requests
import json

def test_webhook_without_signature():
    """Prueba el webhook sin verificación de firma"""
    print("🧪 PROBANDO WEBHOOK SIN VERIFICACIÓN DE FIRMA")
    print("=" * 50)
    
    # URL del webhook
    webhook_url = "http://localhost:8000/webhook"
    
    # Datos de prueba (simulando Twilio)
    test_data = {
        'MessageSid': 'test_message_123',
        'From': 'whatsapp:+1234567890',
        'To': 'whatsapp:+14155238886',
        'Body': 'Hola',
        'AccountSid': 'test_account_123',
        'MessagingServiceSid': 'test_service_123',
        'NumMedia': '0',
        'ProfileName': 'Usuario Test',
        'WaId': '1234567890'
    }
    
    try:
        print(f"📤 Enviando petición a: {webhook_url}")
        print(f"📋 Datos: {test_data}")
        
        # Enviar petición POST
        response = requests.post(webhook_url, data=test_data, timeout=10)
        
        print(f"\n📊 RESULTADO:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ ¡ÉXITO! Webhook funcionando sin verificación de firma")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en puerto 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 TEST WEBHOOK SIN FIRMA")
    print("=" * 40)
    
    # Verificar configuración
    try:
        from app.config import settings
        print(f"🔧 Configuración actual:")
        print(f"   • webhook_verify_signature: {settings.webhook_verify_signature}")
        print(f"   • app_environment: {settings.app_environment}")
        
        if not settings.webhook_verify_signature:
            print("✅ Verificación de firma DESHABILITADA")
        else:
            print("⚠️ Verificación de firma HABILITADA")
            
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
    
    print("\n" + "=" * 40)
    
    # Probar webhook
    test_webhook_without_signature()
    
    print("\n" + "=" * 40)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Si el test es exitoso, envía un mensaje real de WhatsApp")
    print("2. El bot debería responder sin errores de firma")
    print("3. Una vez que funcione, podemos re-habilitar la verificación")

if __name__ == "__main__":
    main() 