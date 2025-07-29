#!/usr/bin/env python3
"""
Script para mostrar la URL correcta que debe configurarse en Twilio Console.
"""
import requests
import json

def check_ngrok_status():
    """Verifica el estado de ngrok y muestra la URL correcta"""
    print("🔍 VERIFICANDO CONFIGURACIÓN DE WEBHOOK")
    print("=" * 50)
    
    try:
        # Intentar obtener la URL de ngrok
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json()['tunnels']
            if tunnels:
                ngrok_url = tunnels[0]['public_url']
                print(f"✅ Ngrok detectado: {ngrok_url}")
                print(f"🌐 URL correcta para Twilio Console: {ngrok_url}/webhook")
                print(f"📋 Método: POST")
                return ngrok_url
            else:
                print("❌ No se encontraron túneles de ngrok activos")
        else:
            print("❌ No se puede conectar a ngrok (puerto 4040)")
            
    except requests.exceptions.ConnectionError:
        print("❌ Ngrok no está ejecutándose")
        print("💡 Ejecuta: ngrok http 8000")
    except Exception as e:
        print(f"❌ Error verificando ngrok: {e}")
    
    return None

def show_twilio_configuration():
    """Muestra la configuración correcta para Twilio Console"""
    print("\n📋 CONFIGURACIÓN PARA TWILIO CONSOLE")
    print("=" * 50)
    
    print("🔧 En Twilio Sandbox Configuration:")
    print("   • When a message comes in:")
    print("     URL: https://cute-kind-dog.ngrok-free.app/webhook")
    print("     Method: POST")
    print("   • Status callback URL: (dejar vacío)")
    print("     Method: GET")
    
    print("\n⚠️ PROBLEMA ACTUAL:")
    print("   • URL en Twilio: https://cute-kind-dog.ngrok-free.app")
    print("   • URL esperada: https://cute-kind-dog.ngrok-free.app/webhook")
    print("   • Diferencia: Falta '/webhook' al final")
    
    print("\n✅ SOLUCIÓN:")
    print("   1. Ve a Twilio Console → Sandbox Configuration")
    print("   2. En 'When a message comes in', cambia la URL a:")
    print("      https://cute-kind-dog.ngrok-free.app/webhook")
    print("   3. Guarda los cambios")
    print("   4. Prueba enviando un mensaje de WhatsApp")

def main():
    """Función principal"""
    print("🚀 DIAGNÓSTICO DE WEBHOOK TWILIO")
    print("=" * 60)
    
    # Verificar ngrok
    ngrok_url = check_ngrok_status()
    
    # Mostrar configuración correcta
    show_twilio_configuration()
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN:")
    print("   El problema es que la URL en Twilio no incluye '/webhook'")
    print("   Cambia la URL en Twilio Console y el error se resolverá")
    print("=" * 60)

if __name__ == "__main__":
    main() 