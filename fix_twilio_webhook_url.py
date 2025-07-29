#!/usr/bin/env python3
"""
Script para arreglar la configuración de webhook en Twilio Console.
"""
import requests
import json

def check_current_ngrok():
    """Verifica la URL actual de ngrok"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json()['tunnels']
            if tunnels:
                return tunnels[0]['public_url']
    except:
        pass
    return "https://cute-kind-dog.ngrok-free.app"  # URL por defecto

def main():
    """Función principal"""
    print("🔧 ARREGLANDO CONFIGURACIÓN DE WEBHOOK TWILIO")
    print("=" * 60)
    
    # Obtener URL actual de ngrok
    ngrok_url = check_current_ngrok()
    correct_webhook_url = f"{ngrok_url}/webhook"
    
    print(f"🌐 URL de ngrok detectada: {ngrok_url}")
    print(f"✅ URL correcta para Twilio: {correct_webhook_url}")
    
    print("\n📋 PASOS PARA ARREGLAR EN TWILIO CONSOLE:")
    print("=" * 50)
    print("1. Ve a https://console.twilio.com/")
    print("2. Navega a Messaging → Try it out → Send a WhatsApp message")
    print("3. En la sección 'Sandbox Configuration':")
    print("4. En 'When a message comes in', cambia la URL de:")
    print(f"   ❌ {ngrok_url}")
    print(f"   ✅ {correct_webhook_url}")
    print("5. Método: POST (mantener)")
    print("6. Guarda los cambios")
    
    print("\n🔍 VERIFICACIÓN:")
    print("=" * 30)
    print("• URL en Twilio debe ser: " + correct_webhook_url)
    print("• URL en código ya está actualizada")
    print("• Método: POST")
    
    print("\n🧪 PRUEBA:")
    print("=" * 20)
    print("1. Guarda los cambios en Twilio")
    print("2. Envía un mensaje de WhatsApp")
    print("3. Verifica que no aparezca 'FIRMA INVÁLIDA'")
    print("4. El bot debería responder correctamente")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DEL PROBLEMA:")
    print("   • Twilio enviaba a: https://cute-kind-dog.ngrok-free.app/")
    print("   • Código esperaba: https://cute-kind-dog.ngrok-free.app/webhook")
    print("   • Solución: Cambiar URL en Twilio Console")
    print("=" * 60)

if __name__ == "__main__":
    main() 