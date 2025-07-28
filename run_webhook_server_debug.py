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
    print("🚀 BOT BRENDA WHATSAPP - MODO DEBUG ACTIVADO")
    print("🔍 Debug activo en: webhook.py, analyze_message_intent.py, openai_client.py, generate_intelligent_response.py, twilio_client.py")
    print("🎯 Flujo: Recepción → Análisis OpenAI → Respuesta → Envío Twilio")
    print("🎮 SERVIDOR INICIANDO...")

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
    
    print(f"📡 Servidor: {config['host']}:{config['port']} | Reload: {config['reload']}")
    print("🌍 Testing: ngrok http 8000 → configurar URL en Twilio Console")
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n💥 Error ejecutando servidor: {e}")
        sys.exit(1)