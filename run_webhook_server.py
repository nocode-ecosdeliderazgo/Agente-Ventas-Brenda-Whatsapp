#!/usr/bin/env python3
"""
Servidor webhook para Bot Brenda - Respuesta automática "Hola"
============================================================

Este script inicia el servidor webhook que:
1. Recibe mensajes de WhatsApp via Twilio
2. Responde automáticamente "Hola" a cualquier mensaje
3. Usa la arquitectura limpia implementada

Para probar:
1. Ejecuta este script
2. Usa ngrok para exponer el webhook públicamente  
3. Configura la URL del webhook en tu consola de Twilio
4. Envía un mensaje WhatsApp a tu número de Twilio

Uso:
    python run_webhook_server.py
"""
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

import uvicorn
from app.config import settings

def main():
    """Función principal para iniciar el servidor."""
    
    # Configurar logging
    logging.basicConfig(
        level=settings.get_log_level(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    print("🚀 INICIANDO SERVIDOR WEBHOOK - BOT BRENDA")
    print("=" * 50)
    print(f"🌍 Entorno: {settings.app_environment}")
    print(f"📱 Número Twilio: {settings.twilio_phone_number}")
    print(f"🔧 Log Level: {settings.log_level}")
    print(f"🔐 Verificar firma: {settings.webhook_verify_signature}")
    print("=" * 50)
    
    if settings.is_development:
        print("\n📝 INSTRUCCIONES PARA DESARROLLO:")
        print("1. Este servidor se ejecutará en http://localhost:8000")
        print("2. Para que Twilio pueda enviar webhooks, necesitas usar ngrok:")
        print("   - Instala ngrok: https://ngrok.com/")
        print("   - En otra terminal ejecuta: ngrok http 8000")
        print("   - Copia la URL https:// que te proporcione ngrok")
        print("   - Ve a tu consola de Twilio y configura esa URL como webhook")
        print("   - La URL completa sería: https://tu-ngrok-url.ngrok.io/webhook/whatsapp")
        print("\n🎯 FUNCIONALIDAD ACTUAL:")
        print("- Recibe cualquier mensaje de WhatsApp")
        print("- Responde automáticamente 'Hola'")
        print("- Ignora mensajes SMS")
        print("- Logs detallados de toda la actividad")
        print("\n🔄 Para probar:")
        print("1. Configura el webhook en Twilio")
        print("2. Envía un mensaje WhatsApp a tu número de Twilio")
        print("3. Deberías recibir 'Hola' como respuesta")
        print("=" * 50)
    
    try:
        logger.info("🌐 Iniciando servidor FastAPI en puerto 8000...")
        
        uvicorn.run(
            "app.presentation.api.webhook:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.is_development,
            log_level=settings.log_level.lower(),
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"💥 Error iniciando servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()