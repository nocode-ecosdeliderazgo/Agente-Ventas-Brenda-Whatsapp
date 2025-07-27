#!/usr/bin/env python3
"""
Script para ejecutar el servidor webhook con debug completo.
Muestra todos los debug prints en la consola para ver el flujo interno.
"""
import os
import sys
import uvicorn
import logging

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_debug_header():
    """Imprime header de debug al iniciar"""
    print("\n" + "="*100)
    print(" " * 25 + "🚀 BOT BRENDA WHATSAPP - MODO DEBUG ACTIVADO 🚀")
    print("="*100)
    print("📋 INFORMACIÓN DE DEBUG:")
    print("   🔍 Verás TODOS los prints de debug internos")
    print("   📁 Archivos con debug: webhook.py, analyze_message_intent.py, openai_client.py,")
    print("                          generate_intelligent_response.py, twilio_client.py")
    print("   📊 Cada debug incluye: [archivo::función] para identificar origen")
    print("   🎯 Flujo completo: Recepción → Análisis OpenAI → Respuesta → Envío Twilio")
    print("="*100)
    print("💡 CONSEJOS:")
    print("   • Envía un mensaje WhatsApp y observa el flujo completo")
    print("   • Busca errores en secciones específicas usando el formato [archivo::función]")
    print("   • Si OpenAI falla, verás el fallback automático")
    print("   • Si PostgreSQL no está disponible, funcionará sin base de datos")
    print("="*100)
    print("🎮 SERVIDOR INICIANDO...\n")

if __name__ == "__main__":
    print_debug_header()
    
    # Configurar logging básico (pero los debug prints seguirán siendo visibles)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configuración del servidor
    config = {
        "app": "app.presentation.api.webhook:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,  # Recarga automática en desarrollo
        "log_level": "info"
    }
    
    print("📡 Configuración del servidor:")
    print(f"   🌐 Host: {config['host']}")
    print(f"   🔌 Puerto: {config['port']}")
    print(f"   🔄 Auto-reload: {config['reload']}")
    print(f"   📊 Log level: {config['log_level']}")
    print()
    
    print("🌍 Para testing local:")
    print("   1. En otra terminal ejecuta: ngrok http 8000")
    print("   2. Copia la URL https://...ngrok.io")
    print("   3. Configúrala en Twilio Console como webhook URL")
    print("   4. Envía un mensaje WhatsApp y observa los debug prints aquí")
    print()
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n💥 Error ejecutando servidor: {e}")
        sys.exit(1)