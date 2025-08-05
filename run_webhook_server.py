#!/usr/bin/env python3
"""
Servidor webhook para el Bot Brenda
====================================

Este script inicia el servidor webhook principal para el Bot Brenda.
Utiliza FastAPI y Uvicorn para levantar un servidor que recibe los 
mensajes de WhatsApp a través de Twilio y los procesa utilizando
la arquitectura limpia del proyecto.

Funcionalidades principales:
1.  Recibe webhooks de Twilio con los mensajes de WhatsApp.
2.  Procesa los mensajes a través de los casos de uso de la aplicación.
3.  Utiliza IA para analizar intenciones y generar respuestas.
4.  Gestiona la memoria y el contexto de la conversación.
5.  Envía respuestas (texto y multimedia) de vuelta al usuario.

Para probar en desarrollo:
1.  Ejecuta este script: `python run_webhook_server.py`
2.  Usa ngrok para exponer el puerto 8000 públicamente: `ngrok http 8000`
3.  Configura la URL de ngrok en la consola de Twilio para tu número de WhatsApp.
4.  Envía un mensaje al número de WhatsApp para interactuar con el bot.

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
        print("- Recibe y procesa mensajes de WhatsApp con IA")
        print("- Mantiene el contexto de la conversación")
        print("- Permite flujos de venta y consulta de cursos")
        print("- Logs detallados de toda la actividad")
        print("\n🔄 Para probar:")
        print("1. Configura el webhook en Twilio")
        print("2. Envía un mensaje WhatsApp a tu número de Twilio")
        print("3. Interactúa con el bot para probar los diferentes flujos")
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