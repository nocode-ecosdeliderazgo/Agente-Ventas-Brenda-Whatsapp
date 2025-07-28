#!/usr/bin/env python3
"""
Script para probar que el servidor webhook funciona correctamente.
"""
import requests
import json
import time

def test_webhook_server():
    """Prueba que el servidor webhook responde correctamente"""
    print("🧪 PRUEBA RÁPIDA DEL SERVIDOR WEBHOOK")
    print("=" * 50)
    
    # URL del servidor local
    webhook_url = "http://localhost:8000/webhook"
    
    # Simular payload de Twilio
    test_payload = {
        "From": "whatsapp:+1234567890",
        "Body": "Hola",
        "MessageSid": "test_message_123",
        "AccountSid": "test_account_123"
    }
    
    try:
        print("📡 Enviando request de prueba...")
        print(f"   URL: {webhook_url}")
        print(f"   Payload: {json.dumps(test_payload, indent=2)}")
        
        # Enviar request POST
        response = requests.post(
            webhook_url,
            data=test_payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        
        print(f"\n📊 RESPUESTA DEL SERVIDOR:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Content: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ ¡SERVIDOR FUNCIONANDO CORRECTAMENTE!")
            print("🚀 El webhook está listo para recibir mensajes de WhatsApp")
        else:
            print("❌ Error en el servidor")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("   Verifica que el servidor esté ejecutándose en puerto 8000")
        print("   Ejecuta: python run_webhook_server_debug.py")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - El servidor no respondió en tiempo")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_server_health():
    """Prueba el endpoint de health check"""
    print("\n🏥 PRUEBA DE HEALTH CHECK")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Health check funcionando")
        else:
            print("❌ Health check falló")
            
    except Exception as e:
        print(f"❌ Error en health check: {e}")

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DEL SERVIDOR WEBHOOK")
    print("=" * 60)
    
    # Esperar un momento para que el servidor se inicie
    print("⏳ Esperando 3 segundos para que el servidor se inicie...")
    time.sleep(3)
    
    # Probar health check
    test_server_health()
    
    # Probar webhook
    test_webhook_server()
    
    print("\n" + "=" * 60)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Configurar ngrok: ngrok http 8000")
    print("2. Configurar webhook en Twilio Console")
    print("3. Probar con mensajes reales de WhatsApp")
    print("=" * 60)

if __name__ == "__main__":
    main() 